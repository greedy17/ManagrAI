<template>
  <PopularWorkflows :config="userCRM === 'SALESFORCE' ? allConfigs.CLOSE_DATE_PASSED : allConfigs.CLOSE_DATE_PASSED_HUBSPOT" />
</template>

<script>
/**
 * Components
 * */
//Internal
import PopularWorkflows from '@/views/settings/alerts/create/templates/PopularWorkflows'
import allConfigs from '../../configs'

export default {
  name: 'CloseDatePassed',
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
