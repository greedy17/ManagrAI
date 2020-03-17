<template>
  <div class="actions">
    LeadActions Component
  </div>
</template>

<script>
export default {
  name: 'LeadActions',
  props: ['lead'],
}
</script>

<style lang="scss" scoped>
.actions {
  width: 765px;
  height: 325px;
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.05);
  border: solid 1px #f2f2f3;
  background-color: #ffffff;
}
</style>
