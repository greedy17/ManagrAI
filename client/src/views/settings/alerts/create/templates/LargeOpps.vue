<template>
  <PopularWorkflows
    :config="userCRM === 'SALESFORCE' ? allConfigs.LARGE_OPPORTUNITIES : allConfigs.LARGE_DEALS_HUBSPOT"
    :largeOpps="true"
    :selectField="true"
  />
</template>

<script>
/**
 * Components
 * */
//Internal
import PopularWorkflows from '@/views/settings/alerts/create/templates/PopularWorkflows'
import allConfigs from '../../configs'

export default {
  name: 'LargeOpportunities',
  components: {
    PopularWorkflows,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      allConfigs,
    }
  },
  computed: {
    userCRM() {
      return this.$store.state.user.crm
    },
  },
}
</script>