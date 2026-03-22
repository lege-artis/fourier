/**
 * Scala Hello World Test
 *
 * A simple test object that demonstrates Scala functionality
 * including string operations, assertions, and functional programming.
 */

object HelloTest {

  /**
   * Main entry point for the hello world test
   */
  def main(args: Array[String]): Unit = {
    println("Starting Scala Hello World Test...")

    // Test 1: Basic string output
    val greeting: String = "Hello, World!"
    println(greeting)
    assert(greeting.nonEmpty)
    assert(greeting.length == 13)

    // Test 2: String comparison
    val expected = "Hello, World!"
    assert(greeting == expected)

    // Test 3: Basic arithmetic
    val a = 5
    val b = 3
    val sum = a + b
    assert(sum == 8)
    println(s"$a + $b = $sum")

    // Test 4: Multiple assertions
    assert(a > b)
    assert(b < a)
    assert(sum > 0)

    // Test 5: String manipulation with string interpolation
    val extendedGreeting = s"$greeting (From Scala)"
    println(extendedGreeting)
    assert(extendedGreeting.contains("Scala"))

    // Test 6: List operations
    val numbers: List[Int] = List(1, 2, 3, 4, 5)
    val sumOfNumbers: Int = numbers.sum
    assert(sumOfNumbers == 15)
    println(s"Sum of $numbers = $sumOfNumbers")

    // Test 7: Functional operations
    val doubled: List[Int] = numbers.map(_ * 2)
    assert(doubled == List(2, 4, 6, 8, 10))
    println(s"Doubled: $doubled")

    // Test 8: Filter operations
    val evens: List[Int] = numbers.filter(_ % 2 == 0)
    assert(evens == List(2, 4))
    println(s"Even numbers: $evens")

    // Test 9: Pattern matching
    val message = testPatternMatching(5)
    println(message)
    assert(message == "Five")

    // Test 10: Case class operations
    val person = Person("Alice", 30)
    println(s"Person: ${person.name}, Age: ${person.age}")
    assert(person.name == "Alice")
    assert(person.age == 30)

    println("All Scala tests passed successfully!")
  }

  /**
   * Test pattern matching functionality
   */
  def testPatternMatching(n: Int): String = n match {
    case 1 => "One"
    case 2 => "Two"
    case 3 => "Three"
    case 4 => "Four"
    case 5 => "Five"
    case _ => "Other"
  }

  /**
   * Simple case class for testing
   */
  case class Person(name: String, age: Int)
}

/**
 * Unit tests for HelloTest
 */
class HelloTestSuite extends org.scalatest.funsuite.AnyFunSuite {

  test("String creation and comparison") {
    val greeting = "Hello, World!"
    assert(greeting == "Hello, World!")
  }

  test("Arithmetic operations") {
    val result = 5 + 3
    assert(result == 8)
  }

  test("List operations") {
    val numbers = List(1, 2, 3, 4, 5)
    assert(numbers.sum == 15)
  }

  test("Functional map operation") {
    val numbers = List(1, 2, 3)
    val doubled = numbers.map(_ * 2)
    assert(doubled == List(2, 4, 6))
  }

  test("Functional filter operation") {
    val numbers = List(1, 2, 3, 4, 5)
    val evens = numbers.filter(_ % 2 == 0)
    assert(evens == List(2, 4))
  }

  test("String contains") {
    val text = "Hello, Scala!"
    assert(text.contains("Scala"))
  }

  test("Case class equality") {
    val person1 = HelloTest.Person("Alice", 30)
    val person2 = HelloTest.Person("Alice", 30)
    assert(person1 == person2)
  }

  test("Pattern matching") {
    val result = HelloTest.testPatternMatching(5)
    assert(result == "Five")
  }
}
