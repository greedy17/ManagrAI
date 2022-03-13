<template>
  <div>
    <div style="max-width: 16vw">
      <div>
        <p style="letter-spacing: 0.25px; font-size: 14px; margin-bottom: 3px">{{ name }}</p>
        <span style="color: #199e54; font-size: 12px">
          {{ accountName ? accountName + ' ' : '--- ' }}
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

<style lang="scss">
@import '@/styles/variables';
@import '@/styles/buttons';
