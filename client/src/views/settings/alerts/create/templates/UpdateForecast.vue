<template>
  <PopularWorkflows :config="userCRM === 'HUBSPOT' ? allConfigs.THIRTY_DAY_PIPELINE_HUBSPOT : allConfigs.THIRTY_DAY_PIPELINE" />
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
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user.crm
    },
  },
}
</script>