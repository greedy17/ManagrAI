<template>
  <div class="pipeline-loader">
    <!-- <section class="flex-row-spreader">
      <div>
        <SkeletonBox style="margin-right: 0.25rem" width="44vw" height="34px" />
      </div>
      <div>
        <SkeletonBox style="margin-right: 0.25rem" width="36vw" height="34px" />
      </div>
    </section>

    <section class="table-sectioned">
      <div style="margin-bottom: 0.05rem">
        <SkeletonBox width="97vw" height="10vh" />
      </div>
      <div style="margin-bottom: 0.1rem">
        <SkeletonBox width="97vw" height="62vh" />
      </div>
    </section> -->

    <!-- <section>
      <div class="loading loading06">
        <span data-text="S">S</span>
        <span data-text="Y">Y</span>
        <span data-text="N">N</span>
        <span data-text="C">C</span>
        <span data-text="I">I</span>
        <span data-text="N">N</span>
        <span data-text="G">G</span>
        &nbsp;
        <span data-text="Y">Y</span>
        <span data-text="O">O</span>
        <span data-text="U">U</span>
        <span data-text="R">R</span>
        &nbsp;
        <span data-text="L">L</span>
        <span data-text="A">A</span>
        <span data-text="T">T</span>
        <span data-text="E">E</span>
        <span data-text="S">S</span>
        <span data-text="T">T</span>
        &nbsp;
        <span data-text="D">D</span>
        <span data-text="A">A</span>
        <span data-text="T">T</span>
        <span data-text="A">A</span>
      </div>
    </section> -->

    <div class="card">
      <h1>Just a moment</h1>
      <p>Pulling in your latest Salesforce data</p>
      <div class="loader"></div>
    </div>
  </div>
</template>

<script>
import SkeletonBox from '@/components/SkeletonBox'

export default {
  name: 'PipelineLoader',
  components: {
    SkeletonBox,
  },
  data() {
    return {}
  },
  methods: {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.pipeline-loader {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 70vh;
}
.table-sectioned {
  height: 76vh;
}
.flex-row-spreader {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
  margin-top: 1rem;
}
// .loading {
//   font-size: 30px;
//   font-family: 'Montserrat', sans-serif;
//   font-weight: 800;
//   text-align: center;
//   span {
//     display: inline-block;
//     margin: 0 -0.05em;
//   }
// }
// .loading06 {
//   span {
//     position: relative;
//     color: $lighter-green;
//     &::after {
//       position: absolute;
//       top: 0;
//       left: 0;
//       content: attr(data-text);
//       color: $dark-green;
//       opacity: 0;
//       transform: rotateY(-90deg);
//       animation: loading06 6s infinite;
//     }
//     @for $i from 1 through 6 {
//       &:nth-child(#{$i + 1})::after {
//         animation-delay: #{$i * 0.2}s;
//       }
//     }
//   }
// }
// @keyframes loading06 {
//   0%,
//   75%,
//   100% {
//     transform: rotateY(-90deg);
//     opacity: 0;
//   }
//   25%,
//   50% {
//     transform: rotateY(0);
//     opacity: 1;
//   }
// }
</style>