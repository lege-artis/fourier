/// Rust Hello World Test
///
/// A simple test program that demonstrates Rust functionality
/// including string operations, assertions, and basic arithmetic.

fn main() {
    println!("Starting Rust Hello World Test...");

    // Test 1: Basic string output
    let greeting = String::from("Hello, World!");
    println!("{}", greeting);
    assert!(!greeting.is_empty());
    assert_eq!(greeting.len(), 13);

    // Test 2: String comparison
    let expected = "Hello, World!";
    assert_eq!(greeting, expected);

    // Test 3: Basic arithmetic
    let a: i32 = 5;
    let b: i32 = 3;
    let sum: i32 = a + b;
    assert_eq!(sum, 8);
    println!("{} + {} = {}", a, b, sum);

    // Test 4: Multiple assertions
    assert!(a > b);
    assert!(b < a);
    assert!(sum > 0);

    // Test 5: String manipulation
    let mut extended_greeting = greeting.clone();
    extended_greeting.push_str(" (From Rust)");
    println!("{}", extended_greeting);
    assert!(extended_greeting.contains("Rust"));

    // Test 6: Array and iteration
    let numbers = [1, 2, 3, 4, 5];
    let sum_of_numbers: i32 = numbers.iter().sum();
    assert_eq!(sum_of_numbers, 15);
    println!("Sum of {:?} = {}", numbers, sum_of_numbers);

    // Test 7: Vector operations
    let mut vec = vec![1, 2, 3];
    vec.push(4);
    vec.push(5);
    assert_eq!(vec.len(), 5);
    println!("Vector: {:?}", vec);

    println!("All Rust tests passed successfully!");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_string_creation() {
        let greeting = String::from("Hello, World!");
        assert_eq!(greeting, "Hello, World!");
    }

    #[test]
    fn test_arithmetic() {
        let result = 5 + 3;
        assert_eq!(result, 8);
    }

    #[test]
    fn test_string_contains() {
        let text = "Hello, Rust!";
        assert!(text.contains("Rust"));
    }

    #[test]
    fn test_vector_operations() {
        let mut vec = vec![1, 2, 3];
        vec.push(4);
        assert_eq!(vec.len(), 4);
        assert_eq!(vec[3], 4);
    }
}
