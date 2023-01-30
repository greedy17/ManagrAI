<template>
  <div>
    <div>
      <div>
        <!-- margin-bottom: 3px; if including account and owner -->
        <p style="letter-spacing: 0.25px; font-size: 13px">{{ name }}</p>
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
</style>