module tb_sync_fifo;
    reg clk;
    reg rst_n;
    reg wr_en;
    reg rd_en;
    reg [7:0] din;
    wire [7:0] dout;
    wire full;
    wire empty;
    wire [2:0] count;

    sync_fifo #(
        .DATA_WIDTH(8),
        .DEPTH(4),
        .ADDR_WIDTH(2)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .wr_en(wr_en),
        .rd_en(rd_en),
        .din(din),
        .dout(dout),
        .full(full),
        .empty(empty),
        .count(count)
    );

    initial begin
        clk = 1'b0;
        forever #5 clk = ~clk;
    end

    task fail;
        input [1023:0] reason;
        begin
            $display("DUTPILOT_FAIL: %0s", reason);
            $fatal;
        end
    endtask

    task expect_flags;
        input exp_empty;
        input exp_full;
        input [2:0] exp_count;
        begin
            #1;
            if (empty !== exp_empty) fail("empty flag mismatch");
            if (full !== exp_full) fail("full flag mismatch");
            if (count !== exp_count) fail("count mismatch");
        end
    endtask

    task push;
        input [7:0] value;
        begin
            @(negedge clk);
            din = value;
            wr_en = 1'b1;
            rd_en = 1'b0;
            @(negedge clk);
            wr_en = 1'b0;
            din = 8'h00;
        end
    endtask

    task pop_expect;
        input [7:0] expected;
        begin
            @(negedge clk);
            wr_en = 1'b0;
            rd_en = 1'b1;
            @(negedge clk);
            rd_en = 1'b0;
            #1;
            if (dout !== expected) begin
                $display("DUTPILOT_FAIL: expected dout %0d, got %0d", expected, dout);
                $fatal;
            end
        end
    endtask

    initial begin
        $dumpfile("waves/wave.vcd");
        $dumpvars(0, tb_sync_fifo);

        rst_n = 1'b0;
        wr_en = 1'b0;
        rd_en = 1'b0;
        din = 8'h00;

        repeat (2) @(negedge clk);
        rst_n = 1'b1;
        expect_flags(1'b1, 1'b0, 3'd0);

        push(8'h11);
        expect_flags(1'b0, 1'b0, 3'd1);
        push(8'h22);
        push(8'h33);
        push(8'h44);
        expect_flags(1'b0, 1'b1, 3'd4);

        push(8'h55);
        expect_flags(1'b0, 1'b1, 3'd4);

        pop_expect(8'h11);
        expect_flags(1'b0, 1'b0, 3'd3);
        pop_expect(8'h22);

        @(negedge clk);
        din = 8'h55;
        wr_en = 1'b1;
        rd_en = 1'b1;
        @(negedge clk);
        wr_en = 1'b0;
        rd_en = 1'b0;
        #1;
        if (dout !== 8'h33) begin
            $display("DUTPILOT_FAIL: simultaneous read expected 51, got %0d", dout);
            $fatal;
        end
        expect_flags(1'b0, 1'b0, 3'd2);

        pop_expect(8'h44);
        pop_expect(8'h55);
        expect_flags(1'b1, 1'b0, 3'd0);

        @(negedge clk);
        rd_en = 1'b1;
        @(negedge clk);
        rd_en = 1'b0;
        expect_flags(1'b1, 1'b0, 3'd0);

        $display("DUTPILOT_PASS");
        $finish;
    end
endmodule
