module tb_counter;
    reg clk;
    reg rst_n;
    reg en;
    wire [3:0] count;

    counter dut (
        .clk(clk),
        .rst_n(rst_n),
        .en(en),
        .count(count)
    );

    initial begin
        clk = 1'b0;
        forever #5 clk = ~clk;
    end

    task expect_count;
        input [3:0] expected;
        begin
            #1;
            if (count !== expected) begin
                $display("DUTPILOT_FAIL: expected count %0d, got %0d", expected, count);
                $fatal;
            end
        end
    endtask

    initial begin
        $dumpfile("waves/wave.vcd");
        $dumpvars(0, tb_counter);

        rst_n = 1'b0;
        en = 1'b0;
        repeat (2) @(negedge clk);
        rst_n = 1'b1;
        expect_count(4'd0);

        en = 1'b1;
        @(negedge clk);
        expect_count(4'd1);

        @(negedge clk);
        expect_count(4'd2);

        @(negedge clk);
        expect_count(4'd3);

        $display("DUTPILOT_PASS");
        $finish;
    end
endmodule
