module tb_adder;
    reg [7:0] a;
    reg [7:0] b;
    wire [8:0] sum;

    adder dut (
        .a(a),
        .b(b),
        .sum(sum)
    );

    initial begin
        $dumpfile("waves/wave.vcd");
        $dumpvars(0, tb_adder);

        a = 8'd2;
        b = 8'd3;
        #1;
        if (sum !== 9'd5) begin
            $display("DUTPILOT_FAIL: expected 5, got %0d", sum);
            $fatal;
        end

        a = 8'd255;
        b = 8'd1;
        #1;
        if (sum !== 9'd256) begin
            $display("DUTPILOT_FAIL: expected 256, got %0d", sum);
            $fatal;
        end

        a = 8'd33;
        b = 8'd66;
        #1;
        if (sum !== 9'd99) begin
            $display("DUTPILOT_FAIL: expected 99, got %0d", sum);
            $fatal;
        end

        $display("DUTPILOT_PASS");
        $finish;
    end
endmodule
