import os

from migen import *

from litex import get_data_mod
from litex.soc.interconnect import wishbone
from litex.soc.cores.cpu import CPU

from migen.fhdl.specials import Tristate

CPU_VARIANTS = ["standard"]


class MC68040(CPU):
    name                 = "mc68040"
    human_name           = "MC68040"
    variants             = CPU_VARIANTS
    data_width           = 32
    endianness           = "big"
    gcc_triple           = "m68k-elf"
    linker_output_format = "elf32-m68k"
    nop                  = "nop"
    io_regions           = {0x80000000: 0x80000000} # origin, length

    @property
    def gcc_flags(self):
        flags = "-march=68040"
        flags += " -D__mc68040__"
        return flags

    def __init__(self, platform, variant="standard"):
        self.platform     = platform
        self.variant      = variant
        self.idbus        = idbus = wishbone.Interface()
        self.periph_buses = [idbus]
        self.memory_buses = []

        self.reset        = Signal()

        self.cpu_ad_i     = Signal(32)
        self.cpu_ad_o     = Signal(32)
        self.cpu_ad_t     = Signal()

        self.cpu_dir      = Signal()
        self.cpu_oe       = Signal()

        self.cpu_siz      = Signal(2)
        self.cpu_tt       = Signal(2)
        self.cpu_rsto     = Signal()
        self.cpu_tip      = Signal()
        self.cpu_ts       = Signal()
        self.cpu_rw       = Signal()

        self.cpu_cdis     = Signal()
        self.cpu_rsti     = Signal()
        self.cpu_irq      = Signal()
        self.cpu_ta       = Signal()

        # # #

        self.cpu_params = dict()

        self.cpu_params.update(
            # clock / reset
            i_clk    = ClockSignal(),
            i_bclk   = ClockSignal("bclk"),
            i_reset  = (ResetSignal() | self.reset),

            # external pads

            o_cpu_ad_i = self.cpu_ad_i,
            i_cpu_ad_o = self.cpu_ad_o,
            o_cpu_ad_t = self.cpu_ad_t,

            o_cpu_dir  = self.cpu_dir,
            o_cpu_oe   = self.cpu_oe,

            i_cpu_siz  = self.cpu_siz,
            i_cpu_tt   = self.cpu_tt,
            i_cpu_rsto = self.cpu_rsto,
            i_cpu_tip  = self.cpu_tip,
            i_cpu_ts   = self.cpu_ts,
            i_cpu_rw   = self.cpu_rw,

            o_cpu_cdis = self.cpu_cdis,
            o_cpu_rsti = self.cpu_rsti,
            o_cpu_irq  = self.cpu_irq,
            o_cpu_ta   = self.cpu_ta,

            # wishbone

            o_wb_cyc_o = idbus.cyc,
            o_wb_stb_o = idbus.stb,
            i_wb_ack_i = idbus.ack,
            o_wb_we_o  = idbus.we,
            o_wb_sel_o = idbus.sel,
            o_wb_adr_o = idbus.adr,
            o_wb_dat_o = idbus.dat_w,
            i_wb_dat_i = idbus.dat_r)

        # add verilog sources
        self.add_sources(platform)

    def set_reset_address(self, reset_address):
        assert reset_address == 0
        self.reset_address = reset_address

    @staticmethod
    def add_sources(platform):
        platform.add_source(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cpuif.v"))

    def add_pads(self, pads):
        for i in range(len(pads.cpu_ad)):
            self.specials += Tristate(
                target = pads.cpu_ad[i],
                o      = self.cpu_ad_i[i],
                oe     = ~self.cpu_ad_t,
                i      = self.cpu_ad_o[i],
            )

            self.comb += [
                pads.cpu_dir.eq(self.cpu_dir),
                pads.cpu_oe.eq(self.cpu_oe),

                self.cpu_siz.eq(pads.cpu_siz),
                self.cpu_tt.eq(pads.cpu_tt),
                self.cpu_rsto.eq(pads.cpu_rsto),
                self.cpu_tip.eq(pads.cpu_tip),
                self.cpu_ts.eq(pads.cpu_ts),
                self.cpu_rw.eq(pads.cpu_rw),

                pads.cpu_cdis.eq(self.cpu_cdis),
                pads.cpu_rsti.eq(self.cpu_rsti),
                pads.cpu_irq.eq(self.cpu_irq),
                pads.cpu_ta.eq(self.cpu_ta),
            ]

    def do_finalize(self):
        self.specials += Instance("cpuif", **self.cpu_params)
