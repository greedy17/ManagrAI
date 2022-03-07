<template>
  <div>
    <div style="max-width: 16vw">
      <div>
        <p style="letter-spacing: 0.25px; font-size: 13px; margin: 0rem">{{ name }}</p>
        <span style="color: #199e54; font-size: 12px">
          {{ accountName ? accountName + ' ' : '--- ' }}
        </span>
      </div>
      <div style="color: #9b9b9b; font-size: 10px">
        <i>owned by {{ owner }}</i>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PipelineRow',
  data() {
    return {}
  },
  methods: {},
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
