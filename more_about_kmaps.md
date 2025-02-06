# Sums, Prodcts, and Circuits of the Same

Even though digital logic circuits are built up out of only two states: zero and one, there's still an enormous amount of emergent complexity as the circuits scale up. This lab is going to give us some practical experience with a few tools to manage and understand this complexity.

## Toy Example

Take for example the following truth table, with four inputs and one output:

| #      | A   | B   | C   | D   | Y   |
| ------ | --- | --- | --- | --- | --- |
| **0**  | 0   | 0   | 0   | 0   | 1   |
| **1**  | 0   | 0   | 0   | 1   | 1   |
| **2**  | 0   | 0   | 1   | 0   | 0   |
| **3**  | 0   | 0   | 1   | 1   | 0   |
| **4**  | 0   | 1   | 0   | 0   | 0   |
| **5**  | 0   | 1   | 0   | 1   | 0   |
| **6**  | 0   | 1   | 1   | 0   | 0   |
| **7**  | 0   | 1   | 1   | 1   | 0   |
| **8**  | 1   | 0   | 0   | 0   | 1   |
| **9**  | 1   | 0   | 0   | 1   | 1   |
| **10** | 1   | 0   | 1   | 0   | 0   |
| **11** | 1   | 0   | 1   | 1   | 0   |
| **12** | 1   | 1   | 0   | 0   | 0   |
| **13** | 1   | 1   | 0   | 1   | 0   |
| **14** | 1   | 1   | 1   | 0   | 1   |
| **15** | 1   | 1   | 1   | 1   | 0   |

Gathering any information about the most efficient way to implement this equation is extremely difficult just by looking at the truth table. You could come up with something like this:

```
Y = (!A & !B & !C & !D) |
    (!A & !B & !C & D) |
    (A & !B & !C & !D) |
    (A & !B & !C & D) |
    (A & B & C & !D)
```

Which *would* work. Effectively, we've encoded each line in the truth table where Y is 1 and or'd together the conditions. While technically correct, you can see how using this method might lead to extremely complicated equations that are hard to read, and even harder to implement. If you were told to build the above logic equation with discrete logic circuits, you would be right to gawk. If you were given quad AND gates, quad NOR gates, and some six input inverters, you would need:

| Logic Element | Count | Number of chips |
| ------------- | ----- | --------------- |
| AND           | 20    | 5               |
| OR            | 5     | 2               |
| NOT           | 9     | 2               |

That's a total of 9 chips to implement the above equation. As we will get to in future labs, this will also have fairly significant propagation delay among many other complications. So... how do we find a simple **and** correct implementation of the above truth table? This is where we introduce our heros: Karnaugh Maps, Minterms, and Maxterms.

## Karnaugh Maps

Karnaugh Maps, from here known as KMaps, are an alternate way of drawing out a truth table that have some extremely interesting properties and allow us to visualize logic equations in a more intuitive way. We transform the table into a two-dimensional array, where the rows/columns are based on our input variables. However, it's not quite just running a divider down the center of the input columns and turning one into the rows the other the columns. In order for the magic of KMaps to work, we need to use something called "Gray Coding".

In the truth table above, we simply counted up in binary from 0 - 15. If we look at the transition from 0 to 1, a single bit changes, the D bit. However, when we move from 1 to 2, two bits change. D goes from `1`->`0`, and C goes from `0`->`1`. This is the essence of what Gray coding solves -- we order the transition so that between any two states, only a single bit changes. Here's what that might look like in the table:

| #      | A   | B   | C   | D   | Y   |
| ------ | --- | --- | --- | --- | --- |
| **0**  | 0   | 0   | 0   | 0   | 1   |
| **1**  | 0   | 0   | 0   | 1   | 1   |
| **3**  | 0   | 0   | 1   | 1   | 0   |
| **2**  | 0   | 0   | 1   | 0   | 0   |
| **6**  | 0   | 1   | 1   | 0   | 0   |
| **7**  | 0   | 1   | 1   | 1   | 0   |
| **5**  | 0   | 1   | 0   | 1   | 0   |
| **4**  | 0   | 1   | 0   | 0   | 0   |
| **12** | 1   | 1   | 0   | 0   | 0   |
| **13** | 1   | 1   | 0   | 1   | 0   |
| **15** | 1   | 1   | 1   | 1   | 0   |
| **14** | 1   | 1   | 1   | 0   | 1   |
| **10** | 1   | 0   | 1   | 0   | 0   |
| **11** | 1   | 0   | 1   | 1   | 0   |
| **9**  | 1   | 0   | 0   | 1   | 1   |
| **8**  | 1   | 0   | 0   | 0   | 1   |

Notice now, how between any two rows, only a single bit changes in the input values. This is still the exact same truth table, just re-ordered to minimize the changes. There's an alternative way to represent this data in a two dimensional array. If we put the four distinct values of AB as the columns and the four distinct values of CD as the rows, we get a 4 x 4 matrix:

| CD/AB  | 00   | 01   | 11   | 10   |
| ------ | ---- | ---- | ---- | ---- |
| **00** | 0000 | 0100 | 1100 | 1000 |
| **01** | 0001 | 0101 | 1101 | 1001 |
| **11** | 0011 | 0111 | 1111 | 1011 |
| **10** | 0010 | 0110 | 1110 | 1010 |

Note in the table above, that between any two adjacent cells, only a single variable/bit changes. Now, shown as the base10 numbers, we can refer to each of those cells by the value they contain:

| CD/AB  | 00  | 01  | 11  | 10  |
| ------ | --- | --- | --- | --- |
| **00** | 0   | 4   | 12  | 8   |
| **01** | 1   | 5   | 13  | 9   |
| **11** | 3   | 7   | 15  | 11  |
| **10** | 2   | 6   | 14  | 10  |

### Minterms and Sums of Products

Since we have 1s in the 0, 1, 14, 8, and 9 entries, we could present this truth table as `f(A,B,C,D) = ∑m(0, 1, 8, 9, 14)`. This simple line conveys the entire truth table without having to draw it out. We can also use this equation to fill out our KMap. Since each cell can be referred to by its value just as the truth table rows can, we can place 1's into the cells of our matrix as told by our minterm equation:

| CD/AB  | 00  | 01  | 11  | 10  |
| ------ | --- | --- | --- | --- |
| **00** | 1   | 0   | 0   | 1   |
| **01** | 1   | 0   | 0   | 1   |
| **11** | 0   | 0   | 0   | 0   |
| **10** | 0   | 0   | 1   | 0   |

At this point all we have done is change how we are representing the exact same truth table. Nothing has changed, just a new way of looking at the information. We can actually derive the exact same complex equation from the introduction by simply looking at this matrix. Encode each cell who's value is `1` as the four variables in that state, then OR the equations together. However, the Gray coding we have used allows us to do something extremely cool. We can wrap up our KMap into a torus, as any square can be warped in three dimensions:

![rectangle to torus](./img/Torus_from_rectangle.gif)

And that gives us some extremely cool adjacency side effects. Take a look at this graphic below that shows how a KMap wrapped into a torus allows us to go around edges and still obey that only a single bit changes between adjacent cells:

<img src="./img/kmap_torus.svg" height="400">

From here we can start grouping similar outputs to minimize our equation. We can think about this like grouping 1's with similar requirements. Let's look at the 1's in position 8 and 9 for now. We can see that they share A = 1, B = 0, and C = 0, but D can be 0 or 1! Since they are adjacent, we can actually turn that into an equation:

```
h = A & !B & !C
```

Think about this like constraining a box around those cells described by AB = 10 and CD = 0X, where X can be 0 or 1. This makes a box surrounding the two 1's in 8 and 9. We can see two other easy boxes we can make, one surrounding 0 and 1, and one around 14:

| CD/AB  | 00  | 01  | 11  | 10  |
| ------ | --- | --- | --- | --- |
| **00** | [1] | 0   | 0   | (1) |
| **01** | [1] | 0   | 0   | (1) |
| **11** | 0   | 0   | 0   | 0   |
| **10** | 0   | 0   | {1} | 0   |

The first group is represented by numbers in (), the second by numbers in [], and the third by numbers in {}. Let's do the same "what's in common" exercise from above to write out all three equations:

```
() = A & !B & !C
[] = !A & !B & !C
{} = A & B & C & !D
Y = () | [] | {}
```

However, this is only part of how far KMaps can go. Since we are dealing with a torus, we can actually include the 1's in the 0 and 1 position in the map, as they are actually adjacent via the join on the left/right edge. Because of the nature of our binary numbers and how the variables only change by 1 bit between each adjacent cells, we can draw boxes of any size where area is a power of 2. That means we can do 1, 2, 4, 8, etc square area boxes. Boxes of size 4 can be 1x4 or 2x2, as long as there are only four contained cells. The same is true of all other sizes.

This gives us many choices to circle our cells. We could actually just do 5 groups of 1 and get the same equations with the naive solution. But this obviously hasn't simplified our equations any, and we spent all this time for nothing. So, we should follow a few simple rules:

1. Don't forget to Gray Code 
1. Make the largest power-of-two boxes that contain only 1's
2. Boxes may overlap
3. Don't make boxes that *only* include 1's that are in other boxes
   - This will not make your equation wrong, just less optimized
4. Don't forget to Gray Code

With this knowledge in hand, let's see if we can improve the equations we get from this KMap. We can see that the groups () and [] can actually join into one! Indeed, just looking at their equations, and using the properties of digital equations, we can see that () and [] actually eliminate the A term when OR'd together. This is supported by the KMap, as if we draw a box that wraps around the left/right edges, we see that the equations have !B and !C in common. That leaves us with the following equations:

| CD/AB  | 00  | 01  | 11  | 10  |
| ------ | --- | --- | --- | --- |
| **00** | (1) | 0   | 0   | (1) |
| **01** | (1) | 0   | 0   | (1) |
| **11** | 0   | 0   | 0   | 0   |
| **10** | 0   | 0   | {1} | 0   |

```
{} = A & B & C & !D
() = !B & !C
Y = () | {}
```

Wow, not only are we down from five equations down to two, one of those equations only has two terms in it! Go ahead, try this yourself, these two equations, when OR'd together, yield the exact same truth table as our naive implementation at the start.

Note: It is convention that the most significant bits of your variable will appear on the columns, and the least significant bits as the rows. HOWEVER this is not required. Your equations will still be completely correct even if you transpose the table.

### Maxterms and Products of Sums

So we briefly touched on minterms in the previous section. We described the truth table with the equation: `f(A,B,C,D) = ∑m(0, 1, 8, 9, 14)`. There's an alternative way to represent a truth table, and that is to encode the location of the `0`s instead if `1`s. This is called the maxterm equation, and would appear like so for our truth table: `f(A,B,C,D) = ΠM(2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 15)`. We can use this to fill in the table with zeros, and all other cells have a `1`. Obviously, this technique would be better used on logic equations that have more ones than zeros. Let's take a quick peek at what this might look like:


| #      | A   | B   | C   | D   | Y   |
| ------ | --- | --- | --- | --- | --- |
| **0**  | 0   | 0   | 0   | 0   | 1   |
| **1**  | 0   | 0   | 0   | 1   | 1   |
| **3**  | 0   | 0   | 1   | 1   | 1   |
| **2**  | 0   | 0   | 1   | 0   | 1   |
| **6**  | 0   | 1   | 1   | 0   | 1   |
| **7**  | 0   | 1   | 1   | 1   | 0   |
| **5**  | 0   | 1   | 0   | 1   | 0   |
| **4**  | 0   | 1   | 0   | 0   | 1   |
| **12** | 1   | 1   | 0   | 0   | 1   |
| **13** | 1   | 1   | 0   | 1   | 0   |
| **15** | 1   | 1   | 1   | 1   | 0   |
| **14** | 1   | 1   | 1   | 0   | 1   |
| **10** | 1   | 0   | 1   | 0   | 1   |
| **11** | 1   | 0   | 1   | 1   | 1   |
| **9**  | 1   | 0   | 0   | 1   | 1   |
| **8**  | 1   | 0   | 0   | 0   | 1   |

In this case, we would have `f(A,B,C,D) = ΠM(5, 7, 13, 15)`. Let's put this into a KMap:

| CD/AB  | 00  | 01  | 11  | 10  |
| ------ | --- | --- | --- | --- |
| **00** | 1   | 1   | 1   | 1   |
| **01** | 1   | 0   | 0   | 1   |
| **11** | 1   | 0   | 0   | 1   |
| **10** | 1   | 1   | 1   | 1   |

Now, if we see a KMap like this, we can either spend the time to circle all the 1's together, which would look like this:

```
h = !B
j = !C & !D
k = C & !D
Y = h | j | k
```

Which gives us three equations. But... what if we just inverted the whole thing?

| CD/AB  | 00  | 01  | 11  | 10  |
| ------ | --- | --- | --- | --- |
| **00** | 0   | 0   | 0   | 0   |
| **01** | 0   | 1   | 1   | 0   |
| **11** | 0   | 1   | 1   | 0   |
| **10** | 0   | 0   | 0   | 0   |

This would let us derive the following equation:

```
!Y = B & D
```

Which we could invert again:

```
Y = !(B & D)
```

Then, using De Morgan's law:

```
Y = !B | !D
```

I know this seems a bit crazy, but try it. Use the three equations from above and the single equation we just derived. They will yield exactly the same results. Now, let's cover the shortcut to getting here if you see a KMap with more ones than zeros. We can do the maxterm version instead, where we group zeros in the exact same way as we group ones, but instead of making sums of products (groups of AND equations OR'd together), we make products of sums (groups of OR equations AND'd together) using De Morgan's law. Let's try on yet another KMap:

| CD/AB  | 00  | 01  | 11  | 10  |
| ------ | --- | --- | --- | --- |
| **00** | 1   | 1   | 1   | 1   |
| **01** | 1   | (0) | (0) | [0] |
| **11** | 1   | (0) | (0) | 1   |
| **10** | 1   | 1   | 1   | 1   |

We can circle two groups in this KMap. The () group shares B = 1 and D = 1. The [] group has A = 1, B = 0, C = 0, D = 1. However, since we are circling zeros, we must invert each of these terms and use De Morgan's law to expand them:

```
[] = (!A | B | C | D)
() = (!B | !D)
Y = [] & ()
```

Notice now how each of the smaller equations is only OR, and they are AND'd together to get our output equation. This is how you derive the Sum of Products equation from a KMap.
