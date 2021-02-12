<template>
  <div class="container">
    <div class="box">
      <div class="box__tab-header">
        <div
          class="box__tab"
          :class="{ 'box__tab--active': selectedTab == 'MEETING_REVIEW' }"
          @click="toggleSelectedTab('MEETING_REVIEW')"
        >
          Meeting Review Form
        </div>
        <div
          class="box__tab"
          :class="{ 'box__tab--active': selectedTab == 'CREATE' }"
          @click="toggleSelectedTab('CREATE')"
        >
          Create Form
        </div>
        <div
          class="box__tab"
          :class="{ 'box__tab--active': selectedTab == 'UPDATE' }"
          @click="toggleSelectedTab('UPDATE')"
        >
          Update Form
        </div>
      </div>
      <div class="box__content">
        <template v-if="formByType">
          {{ formByType.resource }}
          <p>
            <i
              >Required Fields have been pre-filled as part of the form, add or remove additional
              fields</i
            >
            <br />
            <strong>Additional Validations may apply for your Salesforce Resources</strong
            ><button>Click Here</button><strong>to view them</strong>
          </p>
          <CustomSlackForm :customForm="formByType" :formType="selectedTab" />
        </template>
        <template v-else>
          <p>
            <i
              >We are currently gathering your fields and creating your forms, please check back in
              a couple of minutes</i
            >
          </p>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import CustomSlackForm from '../CustomSlackForm'
import { mapState } from 'vuex'
export default {
  name: 'FormSettings',
  components: { CustomSlackForm },
  data() {
    return {
      forms: [],
      isLoading: false,
      selectedTab: 'MEETING_REVIEW',
    }
  },
  async created() {
    console.log('niether')
  },
  computed: {
    ...mapState(['user']),
    formByType() {
      let form = this.forms.find(form => form.formType == this.selectedTab)

      if (form && typeof form != undefined) {
        return form
      }
      return null
    },
  },
  methods: {
    toggleSelectedTab(tab) {
      this.selectedTab = tab
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
@import '@/styles/emails';
@import '@/styles/sidebars';
</style>
