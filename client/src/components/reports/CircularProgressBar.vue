<template>
  <div ref="progressPieChart" class="progress-pie-chart" data-percent="43">
    <div class="ppc-progress">
      <div ref="ppcProgressFill" class="ppc-progress-fill"></div>
    </div>
    <div class="ppc-percents">
      <div class="pcc-percents-wrapper"></div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CircularProgressBar',
  props: {
    percent: {
      type: Number,
      required: true,
    },
  },
  created() {
    let ppc = this.$refs.progressPieChart
    let deg = (360 * this.percent) / 100
    if (this.percent > 50) {
      ppc.addClass('gt-50')
    }
    this.$refs.ppcProgressFill.css('transform', 'rotate(' + deg + 'deg)')
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

@mixin circle($size) {
  content: '';
  position: absolute;
  border-radius: 50%;
  left: calc(50% - #{$size/2});
  top: calc(50% - #{$size/2});
  width: $size;
  height: $size;
}

$size: 200px;
.progress-pie-chart {
  width: $size;
  height: $size;
  border-radius: 50%;
  background-color: #e5e5e5;
  position: relative;
  &.gt-50 {
    background-color: $dark-green;
  }
}
.ppc-progress {
  @include circle($size);
  clip: rect(0, $size, $size, #{$size/2});
  .ppc-progress-fill {
    @include circle($size);
    clip: rect(0, #{$size/2}, $size, 0);
    background: $dark-green;
    transform: rotate(60deg);
  }
  .gt-50 & {
    clip: rect(0, #{$size/2}, $size, 0);
    .ppc-progress-fill {
      clip: rect(0, $size, $size, #{$size/2});
      background: #e5e5e5;
    }
  }
}
.ppc-percents {
  @include circle(#{$size/1.15});
  background: #fff;
  text-align: center;
  display: table;
  span {
    display: block;
    font-size: 2.6em;
    font-weight: bold;
    color: $dark-green;
  }
}
.pcc-percents-wrapper {
  display: table-cell;
  vertical-align: middle;
}

// body {
//   font-family: Arial;
//   background: #f7f7f7;
// }
.progress-pie-chart {
  margin: 50px auto 0;
}
</style>
