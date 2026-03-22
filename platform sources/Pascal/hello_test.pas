program HelloTest;

{
  Pascal Hello World Test

  A simple test program that demonstrates Free Pascal functionality
  including string operations, assertions, and basic data structures.
}

uses
  SysUtils,
  Classes;

const
  EXPECTED_GREETING = 'Hello, World!';

var
  greeting: String;
  a, b, sumResult: Integer;
  i: Integer;
  numbers: array[1..5] of Integer;
  arraySum: Integer;
  extendedGreeting: String;
  testsPassed: Integer;
  testsFailed: Integer;

{
  Assertion helper procedure
}
procedure AssertEqual(actual, expected: Integer; message: String);
begin
  if actual <> expected then
  begin
    WriteLn('FAILED: ' + message);
    WriteLn('  Expected: ', expected);
    WriteLn('  Actual: ', actual);
    Inc(testsFailed);
  end
  else
  begin
    WriteLn('PASSED: ' + message);
    Inc(testsPassed);
  end;
end;

{
  String assertion helper procedure
}
procedure AssertStringEqual(actual, expected: String; message: String);
begin
  if actual <> expected then
  begin
    WriteLn('FAILED: ' + message);
    WriteLn('  Expected: ' + expected);
    WriteLn('  Actual: ' + actual);
    Inc(testsFailed);
  end
  else
  begin
    WriteLn('PASSED: ' + message);
    Inc(testsPassed);
  end;
end;

{
  Boolean assertion helper procedure
}
procedure AssertTrue(condition: Boolean; message: String);
begin
  if not condition then
  begin
    WriteLn('FAILED: ' + message);
    Inc(testsFailed);
  end
  else
  begin
    WriteLn('PASSED: ' + message);
    Inc(testsPassed);
  end;
end;

{
  Count even numbers in array
}
function CountEven(var arr: array of Integer): Integer;
var
  count, i: Integer;
begin
  count := 0;
  for i := Low(arr) to High(arr) do
  begin
    if arr[i] mod 2 = 0 then
      Inc(count);
  end;
  CountEven := count;
end;

{
  Calculate sum of array
}
function SumArray(var arr: array of Integer): Integer;
var
  sum, i: Integer;
begin
  sum := 0;
  for i := Low(arr) to High(arr) do
    sum := sum + arr[i];
  SumArray := sum;
end;

{
  Find maximum value in array
}
function MaxArray(var arr: array of Integer): Integer;
var
  max, i: Integer;
begin
  max := arr[Low(arr)];
  for i := Low(arr) + 1 to High(arr) do
  begin
    if arr[i] > max then
      max := arr[i];
  end;
  MaxArray := max;
end;

{
  Find minimum value in array
}
function MinArray(var arr: array of Integer): Integer;
var
  min, i: Integer;
begin
  min := arr[Low(arr)];
  for i := Low(arr) + 1 to High(arr) do
  begin
    if arr[i] < min then
      min := arr[i];
  end;
  MinArray := min;
end;

{
  Main program
}
begin
  testsPassed := 0;
  testsFailed := 0;

  WriteLn('Starting Pascal Hello World Test...');
  WriteLn('');

  { Test 1: Basic string output }
  greeting := EXPECTED_GREETING;
  WriteLn(greeting);
  AssertStringEqual(greeting, EXPECTED_GREETING, 'String greeting test');

  { Test 2: String length }
  AssertEqual(Length(greeting), 13, 'String length test');

  { Test 3: Basic arithmetic }
  a := 5;
  b := 3;
  sumResult := a + b;
  WriteLn(IntToStr(a) + ' + ' + IntToStr(b) + ' = ' + IntToStr(sumResult));
  AssertEqual(sumResult, 8, 'Arithmetic test');

  { Test 4: Comparison operations }
  AssertTrue(a > b, 'Comparison test a > b');
  AssertTrue(b < a, 'Comparison test b < a');
  AssertTrue(sumResult > 0, 'Comparison test sum > 0');

  { Test 5: String concatenation }
  extendedGreeting := greeting + ' (From Pascal)';
  WriteLn(extendedGreeting);
  AssertTrue(Pos('Pascal', extendedGreeting) > 0, 'String contains test');

  { Test 6: Array initialization }
  numbers[1] := 1;
  numbers[2] := 2;
  numbers[3] := 3;
  numbers[4] := 4;
  numbers[5] := 5;

  { Test 7: Array sum }
  arraySum := SumArray(numbers);
  WriteLn('Sum of [1, 2, 3, 4, 5] = ' + IntToStr(arraySum));
  AssertEqual(arraySum, 15, 'Array sum test');

  { Test 8: Array iteration }
  WriteLn('Array elements: ');
  for i := Low(numbers) to High(numbers) do
  begin
    WriteLn('  numbers[' + IntToStr(i) + '] = ' + IntToStr(numbers[i]));
  end;

  { Test 9: Count even numbers }
  AssertEqual(CountEven(numbers), 2, 'Count even numbers test');

  { Test 10: Array min/max }
  AssertEqual(MaxArray(numbers), 5, 'MaxArray test');
  AssertEqual(MinArray(numbers), 1, 'MinArray test');

  WriteLn('');
  WriteLn('========================================');
  WriteLn('Test Results:');
  WriteLn('  Tests Passed: ' + IntToStr(testsPassed));
  WriteLn('  Tests Failed: ' + IntToStr(testsFailed));
  WriteLn('========================================');

  if testsFailed = 0 then
  begin
    WriteLn('All Pascal tests passed successfully!');
    ExitCode := 0;
  end
  else
  begin
    WriteLn('Some tests failed!');
    ExitCode := 1;
  end;
end.
