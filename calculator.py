def calculator():
    while True:
        print("\n=== Simple Calculator ===")
        try:
            num1 = float(input("First number: "))
            num2 = float(input("Second number: "))
        except ValueError:
            print("→ Invalid number. Try again.")
            continue
        
        print("Operations:")
        print(" 1) Add (+)")
        print(" 2) Subtract (-)")
        print(" 3) Multiply (*)")
        print(" 4) Divide (/)")
        print(" 5) Exponent (^)")
        print(" 6) Modulo (%)")
        choice = input("Choice [1–6]: ").strip()

        if choice == '1':
            result, op = num1 + num2, '+'
        elif choice == '2':
            result, op = num1 - num2, '-'
        elif choice == '3':
            result, op = num1 * num2, '*'
        elif choice == '4':
            if num2 == 0:
                print("→ Error: division by zero."); continue
            result, op = num1 / num2, '/'
        elif choice == '5':
            result, op = num1 ** num2, '^'
        elif choice == '6':
            if num2 == 0:
                print("→ Error: modulo by zero."); continue
            result, op = num1 % num2, '%'
        else:
            print("→ Invalid choice."); continue

        print(f"→ Result: {num1} {op} {num2} = {result}")

        if input("Press 'q' to quit, Enter to continue: ").lower() == 'q':
            break

if __name__ == "__main__":
    calculator()
