<template>
  <PopularWorkflows
    :config="
      userCRM == 'HUBSPOT' ? allConfigs.CLOSING_NEXT_MONTH_HUBSPOT : allConfigs.CLOSING_NEXT_MONTH
    "
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
  name: 'ClosingNextMonth',
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
