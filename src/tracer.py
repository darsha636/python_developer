import sys
import os
import storage

class Tracer:
    def __init__(self, conn):
        self.conn = conn
        # We store the previous state (snapshot) of locals for each frame.
        # Key: id(frame), Value: dict mapping variable_name -> last seen value
        self.frame_states = {}

    def trace_dispatch(self, frame, event, arg):
        """
        The main trace function installed via sys.settrace().
        - frame: The current stack frame containing execution state (e.g., locals, line number).
        - event: A string indicating the event type ('call', 'line', 'return', 'exception', etc.).
        - arg: Additional info, such as the return value for a 'return' event.
        """
        if event == 'call':
            # Initialize a new snapshot dictionary for this new frame
            self.frame_states[id(frame)] = {}
            # Return ourselves to continue tracing lines inside this frame
            return self.trace_dispatch
            
        elif event == 'line':
            # Get current execution line and the function name
            # For top-level code, frame.f_code.co_name is '<module>'
            line_no = frame.f_lineno
            func_name = frame.f_code.co_name
            
            # frame.f_locals is a dictionary of the local variables currently in scope
            current_locals = frame.f_locals
            prev_locals = self.frame_states.get(id(frame), {})
            
            # Compare current locals with our previous snapshot to detect deltas
            for var_name, value in current_locals.items():
                # Skip python internal/magic variables
                if var_name.startswith('__'):
                    continue
                
                # Determine if the variable is new or its value has changed
                try:
                    changed = var_name not in prev_locals or prev_locals[var_name] != value
                except Exception:
                    # Fallback in case of objects that don't support standard equality (like DataFrames)
                    changed = True
                    
                if changed:
                    # Log the delta using our storage engine
                    storage.record_event(self.conn, line_no, var_name, value, func_name)
                    # Update our snapshot
                    prev_locals[var_name] = value
                    
            self.frame_states[id(frame)] = prev_locals
            return self.trace_dispatch
            
        elif event == 'return':
            # Check for any final variable assignments before the function returns
            line_no = frame.f_lineno
            func_name = frame.f_code.co_name
            current_locals = frame.f_locals
            prev_locals = self.frame_states.get(id(frame), {})
            
            for var_name, value in current_locals.items():
                if var_name.startswith('__'):
                    continue
                try:
                    changed = var_name not in prev_locals or prev_locals[var_name] != value
                except Exception:
                    changed = True
                
                if changed:
                    storage.record_event(self.conn, line_no, var_name, value, func_name)
            
            # Cleanup the frame state when the function returns to avoid memory bloat
            if id(frame) in self.frame_states:
                del self.frame_states[id(frame)]
            return self.trace_dispatch
            
        return self.trace_dispatch


def run_with_trace(file_path):
    """
    Executes the given Python file with the tracer enabled.
    Returns a SQLite connection to the in-memory database containing the recorded events.
    """
    # 1. Set up a fresh in-memory storage connection
    conn = storage.create_connection(in_memory=True)
    tracer = Tracer(conn)
    
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()
        
    code = compile(source, file_path, "exec")
    
    # We use a custom globals dict so the script runs in its own namespace
    global_env = {"__name__": "__main__", "__file__": file_path}
    
    # 2. Install the trace function
    sys.settrace(tracer.trace_dispatch)
    
    # 3. Execute the target script
    try:
        exec(code, global_env)
    except Exception as e:
        sys.settrace(None)
        print(f"Error while tracing script: {type(e).__name__}: {e}")
    finally:
        # 4. Always remove the trace function, even if the script crashes
        sys.settrace(None)
        
    return conn

def main():
    if len(sys.argv) < 2:
        print("Usage: python tracer.py <target_file.py>")
        sys.exit(1)
        
    target_file = sys.argv[1]
    
    if not os.path.exists(target_file):
        print(f"Error: File '{target_file}' not found.")
        sys.exit(1)
        
    print(f"Tracing '{target_file}'...\n")
    conn = run_with_trace(target_file)
    
    events = storage.get_all_events(conn)
    
    if not events:
        print("No events recorded.")
        return
        
    # Print the recorded events in a table
    print(f"{'Step':<5} | {'Line':<5} | {'Function':<12} | {'Variable':<15} | {'Value':<20} | {'Type'}")
    print("-" * 80)
    for row in events:
        # row structure: id, step, timestamp, line_number, function_name, variable_name, variable_value, value_type
        _, step, _, line, func, var, val, vtype = row
        print(f"{step:<5} | {line:<5} | {func:<12} | {var:<15} | {val:<20} | {vtype}")

if __name__ == "__main__":
    main()
