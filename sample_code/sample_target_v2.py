def calculate_sum(limit):
    total = 0
    for i in range(limit):
        total += i
    return total

def main():
    target = 5
    result = calculate_sum(target)
    final_message = "Done"

if __name__ == "__main__":
    main()
