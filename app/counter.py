# AOS-STRESS-001 Implementation
# Rules: No assignments outside recursion, no local files.

def count(current, target):
    if current > target:
        return
    print(current)
    count(current + 1, target)

if __name__ == "__main__":
    count(1, 3)
