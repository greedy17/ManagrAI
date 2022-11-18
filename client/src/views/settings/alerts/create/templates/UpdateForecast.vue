<template>
  <PopularWorkflows :config="userCRM === 'SALESFORCE' ? allConfigs.NINETY_DAY_PIPELINE : allConfigs.NINETY_DAY_PIPELINE_HUBSPOT" />
</template>

<script>
/**
 * Components
 * */
//Internal
import PopularWorkflows from '@/views/settings/alerts/create/templates/PopularWorkflows'
import allConfigs from '../../configs'

export default {
  name: '90DayPipeline',
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