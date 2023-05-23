<template>
  <div>
    <div v-if="dataType === 'TextArea' || dataType === 'String'">
      <textarea :name="apiName" rows="1" />
    </div>
    <!-- <span>{{ dataType }}</span>
    <span>{{ apiName }}</span> -->
  </div>
</template>

<script>
export default {
  name: 'InlineFieldEditor',

  props: {
    dataType: {
      type: String,
    },
    apiName: {
      type: String,
    },
  },
}
</script>

<style lang="scss" scoped>
</style>