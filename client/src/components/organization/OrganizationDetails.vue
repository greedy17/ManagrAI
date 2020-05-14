<template>
  <div class="organization-container">
    <div class="details-card">
      <span>{{ organization.name }}</span>
    </div>
  </div>
</template>
<script>
export default {
  name: 'OrganizationDetails',
  props: {
    organization: {
      type: Object,
      required: true,
    },
  },
}
</script>
