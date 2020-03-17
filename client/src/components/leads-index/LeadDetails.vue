<template>
  <div class="lead-details">Showing LeadDetails Component for {{ lead.name }}...</div>
</template>

<script>
export default {
  name: 'LeadDetails',
  props: ['lead'],
}
</script>

<style lang="scss" scoped>
.lead-details {
  padding-left: 4%;
}
</style>
