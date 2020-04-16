<template>
  <label class="toggle">
    <input type="checkbox" class="toggle" v-model="donationCart.tipEveryTime" />
    <div>
      <div></div>
    </div>
  </label>
</template>

<script>
export default {
  name: 'ToggleCheckBox',
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';
</style>
