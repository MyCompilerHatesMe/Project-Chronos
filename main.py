from modules import text_reconstruction
import sys

fragment = input("Enter the fragmented information: ")
reconstruction = text_reconstruction(fragment)


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("Usage: python main.py [option]")
            print("Options:\n--help -h : Show this help message\n--file -f : Output to a file\n")
            print("By default, the output will be printed to the console.")
            sys.exit(0)
        elif sys.argv[1] == "--file" or sys.argv[1] == "-f":
            with open("reconstruction.txt", "w") as f:
                f.write(reconstruction)
    else:
        print(reconstruction)
            
            
if __name__ == "__main__":
    main()