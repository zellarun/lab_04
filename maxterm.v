module maxterm (
    input A, B, C, D,
    output Y
);

assign Y = (~B | ~D) & (~A | B | C) & (~A | ~D) & (B | C | D);// Enter your equation here

endmodule
