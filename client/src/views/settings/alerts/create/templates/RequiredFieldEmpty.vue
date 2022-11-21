<template>
  <PopularWorkflows :selectField="true" :config="userCRM === 'HUBSPOT' ? allConfigs.REQUIRED_FIELD_EMPTY_HUBSPOT : allConfigs.REQUIRED_FIELD_EMPTY" />
</template>

<script>
/**
 * Components
 * */
//Internal
import PopularWorkflows from '@/views/settings/alerts/create/templates/PopularWorkflows'
import allConfigs from '../../configs'

export default {
  name: 'RequiredFieldEmpty',
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
