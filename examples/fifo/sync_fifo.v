module sync_fifo #(
    parameter DATA_WIDTH = 8,
    parameter DEPTH = 4,
    parameter ADDR_WIDTH = 2
) (
    input  wire                  clk,
    input  wire                  rst_n,
    input  wire                  wr_en,
    input  wire                  rd_en,
    input  wire [DATA_WIDTH-1:0] din,
    output reg  [DATA_WIDTH-1:0] dout,
    output wire                  full,
    output wire                  empty,
    output reg  [ADDR_WIDTH:0]   count
);
    reg [DATA_WIDTH-1:0] mem [0:DEPTH-1];
    reg [ADDR_WIDTH-1:0] wr_ptr;
    reg [ADDR_WIDTH-1:0] rd_ptr;

    wire do_write = wr_en && !full;
    wire do_read = rd_en && !empty;

    assign full = (count == DEPTH[ADDR_WIDTH:0]);
    assign empty = (count == {ADDR_WIDTH + 1{1'b0}});

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr <= {ADDR_WIDTH{1'b0}};
            rd_ptr <= {ADDR_WIDTH{1'b0}};
            count <= {ADDR_WIDTH + 1{1'b0}};
            dout <= {DATA_WIDTH{1'b0}};
        end else begin
            if (do_write) begin
                mem[wr_ptr] <= din;
                wr_ptr <= wr_ptr + {{ADDR_WIDTH - 1{1'b0}}, 1'b1};
            end

            if (do_read) begin
                dout <= mem[rd_ptr];
                rd_ptr <= rd_ptr + {{ADDR_WIDTH - 1{1'b0}}, 1'b1};
            end

            case ({do_write, do_read})
                2'b10: count <= count + {{ADDR_WIDTH{1'b0}}, 1'b1};
                2'b01: count <= count - {{ADDR_WIDTH{1'b0}}, 1'b1};
                default: count <= count;
            endcase
        end
    end
endmodule
