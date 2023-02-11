<template>
  <div>
    <div>
      <div>
        <!-- margin-bottom: 3px; if including account and owner -->
        <!-- <p>{{ hovering ? name : truncate(name, 20) }}</p> -->
        <p class="pipeline-name__background">{{ name ? name : 'N/A' }}</p>
        <!-- <span v-if="userCRM === 'SALESFORCE'" style="color: #199e54; font-size: 12px" :class="!accountName ? 'gray' : ''">
          {{ accountName ? accountName + ' ' : 'No Account ' }}
        </span> -->
      </div>
      <!-- <div style="color: #9b9b9b; font-size: 11px; margin-top: 3px">owned by {{ owner }}</div> -->
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
  methods: {
    truncate(text, max) {
      return `${text.slice(0, max)} ${text.length > max ? '...' : ''}`
    },
  },
  computed: {
    // userCRM() {
    //   return this.$store.state.user.crm
    // },
  },
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.gray {
  color: $very-light-gray !important;
}

<<<<<<< HEAD
.pipeline-name {
  &__background {
    background-color: $soft-gray;
    padding: 4px;
    border-radius: 4px;
  }
=======
.gray-section {
  background-color: $off-white;
  padding: 6px 8px;
  border-radius: 4px;
  width: fit-content;
>>>>>>> 91e96476eb1e1ca325c1e7db3ddb8bdfee324e6d
}
</style>