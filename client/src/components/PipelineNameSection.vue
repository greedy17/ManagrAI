<template>
  <div>
    <div style="max-width: 16vw">
      <div>
        <p style="letter-spacing: 0.25px; font-size: 14px; margin-bottom: 3px">{{ name }}</p>
        <span style="color: #199e54; font-size: 12px" :class="!accountName ? 'gray' : ''">
          {{ accountName ? accountName + ' ' : 'No Account ' }}
        </span>
      </div>
      <div style="color: #9b9b9b; font-size: 11px; margin-top: 3px">owned by {{ owner }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PipelineNameSection',
  data() {
    return {}
  },
  props: {
    name: {
      type: String,
    },
    accountName: {
      type: String,
    },
    owner: {
      type: String,
    },
  },
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.gray {
  color: $very-light-gray !important;
}
</style>