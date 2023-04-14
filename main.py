def hanoi(n, source, target, auxiliary):
    if n > 0:
        # Move n-1 discs from source to auxiliary peg, using target peg as temporary storage
        hanoi(n-1, source, auxiliary, target)
        
        # Move the nth disc from source to target peg
        print(f"Move disc {n} from {source} to {target}")
        
        # Move the n-1 discs from auxiliary to target peg, using source peg as temporary storage
        hanoi(n-1, auxiliary, target, source)


def main():
    # Request user input for the number of discs
    num_discs = int(input("Enter the number of discs: "))

    # Call the hanoi function with the specified number of discs and peg names (A, B, C)
    hanoi(num_discs, 'A', 'C', 'B')

    # Wait for user input before closing the script
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
