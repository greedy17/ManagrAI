<template>
  <div class="pipeline-loader">
    <section class="flex-row-spreader">
      <div>
        <SkeletonBox style="margin-right: 0.25rem" width="150px" height="30px" />
        <SkeletonBox style="margin-right: 0.25rem" width="300px" height="30px" />
      </div>
      <div>
        <SkeletonBox style="margin-right: 0.25rem" width="150px" height="30px" />
        <SkeletonBox width="150px" height="30px" />
      </div>
    </section>

    <section class="table-sectioned">
      <div style="margin-bottom: 0.05rem">
        <SkeletonBox width="97vw" height="10vh" />
      </div>
      <div style="margin-bottom: 0.1rem">
        <SkeletonBox width="97vw" height="62vh" />
      </div>
    </section>
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

<style lang="scss">
@import '@/styles/variables';
@import '@/styles/buttons';

.pipeline-loader {
  margin-top: 4rem;
  padding: 0.5rem;
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
</style>