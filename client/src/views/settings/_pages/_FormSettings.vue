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
        <template v-if="formsByType.length">
          <p>
            <i
              >Required Fields have been pre-filled as part of the form, add or remove additional
              fields</i
            >
            <br />
            <strong>Additional Validations may apply for your Salesforce Resources</strong
            ><button @click="showValidations = !showValidations">Click Here</button
            ><strong>to view them</strong>
          </p>

          <CustomSlackForm
            :show-validations="showValidations"
            :customForm="selectedForm"
            :formType="selectedTab"
            :resource="resource"
            v-on:update:selectedForm="updateForm($event)"
          />
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
import SlackOAuth, { salesforceFields } from '@/services/slack'
export default {
  name: 'FormSettings',
  components: { CustomSlackForm },
  data() {
    return {
      allForms: [],
      formsByType: [],
      isLoading: false,
      selectedTab: 'MEETING_REVIEW',
      resource: 'Opportunity',
      selectedForm: null,
      showValidations: false,
    }
  },
  watch: {},
  async created() {
    try {
      this.allForms = await SlackOAuth.api.getOrgCustomForm()

      this.formsByType = this.allForms.filter(f => {
        return f['resource'] == this.resource
      })

      this.toggleSelectedTab('MEETING_REVIEW')
    } catch (error) {
      console.log(error)
    }
  },
  computed: {
    ...mapState(['user']),
  },
  methods: {
    toggleSelectedTab(tab) {
      this.selectedTab = tab
      let form = this.formsByType.find(f => f.formType == tab)

      if (form && typeof form != undefined) {
        this.selectedForm = form
      } else this.selectedForm = null
    },
    updateForm(event) {
      this.selectedForm = event
      let index = this.formsByType.findIndex(f => f.id == this.selectedForm.id)

      if (~index) {
        this.formsByType[index] = this.selectedForm
        this.formsByType = [...this.formsByType]
      }
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
