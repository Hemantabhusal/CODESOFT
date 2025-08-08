import secrets
import string

def generate_password(length: int) -> str:
    if length < 5:
        raise ValueError("Password length must be at least 5")

    charset = (
        string.ascii_lowercase +
        string.ascii_uppercase +
        string.digits +
        string.punctuation
    )
    return ''.join(secrets.choice(charset) for _ in range(length))

def main():
    print("=== Strong Password Generator ===")
    try:
        length = int(input("Enter desired password length: ").strip())
    except ValueError:
        print("Error: Please enter a valid integer for length.")
        return

    try:
        pwd = generate_password(length)
    except ValueError as e:
        print(f"Error: {e}")
        return

    print("\nGenerated password:")
    print(pwd)

if __name__ == "__main__":
    main()
