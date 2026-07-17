import sys

def trace_function(frame, event, arg):
    """
    frame: current stack frame (code object, line number, locals, etc.)
    event: 'call', 'line', 'return', 'exception'
    arg:   event ke hisaab se extra info (return value, exception info, etc.)
    """
    filename = frame.f_code.co_filename
    func_name = frame.f_code.co_name
    line_no = frame.f_lineno

    if event == 'call':
        print(f"[CALL]   -> {func_name}() | file: {filename} | line: {line_no}")
        # IMPORTANT: 'call' event se local trace function return karna hoga
        # warna is function ke andar 'line' events fire hi nahi honge
        return trace_function

    elif event == 'line':
        print(f"[LINE]   {func_name}() | line {line_no}")

    elif event == 'return':
        print(f"[RETURN] <- {func_name}() | line {line_no} | return_value: {arg}")

    return trace_function


def sample_target(a, b):
    x = a + b
    y = x * 2
    return y


def another_function():
    result = sample_target(3, 4)
    print("Result:", result)


if __name__ == "__main__":
    sys.settrace(trace_function)
    another_function()
    sys.settrace(None)   # tracing band karna zaroori hai, warna overhead chalta rahega