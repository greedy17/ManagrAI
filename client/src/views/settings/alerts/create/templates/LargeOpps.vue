<template>
  <PopularWorkflows
    :config="userCRM === 'HUBSPOT' ? allConfigs.LARGE_DEALS_HUBSPOT : allConfigs.LARGE_OPPORTUNITIES"
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
import { decryptData } from '../../../../../encryption'

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
      const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return decryptedUser.crm
    },
  },
}
</script>