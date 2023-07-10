<template>
  <PopularWorkflows
    :config="userCRM === 'HUBSPOT' ? allConfigs.EMPTY_FIELD_HUBSPOT : allConfigs.EMPTY_FIELD"
    :selectField="true"
    :isEmpty="true"
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
  name: 'EmptyField',
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