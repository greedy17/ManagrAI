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
        <template v-if="selectedForm">
          {{ selectedForm.resource }}
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
            v-on:update:selectedForm="fnTest($event)"
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
      selectedTab: null,
      resource: 'Opportunity',
      selectedForm: null,
      showValidations: false,
    }
  },
  watch: {
    selectedTab: {
      immediate: true,
      handler(val) {
        let form = this.formsByType
          .filter(form => form['resource'] == this.resource)
          .find(f => f.formType == val)

        if (form && typeof form != undefined) {
          this.selectedForm = form
        } else this.selectedForm = null
      },
    },
  },
  async created() {
    try {
      this.allForms = await SlackOAuth.api.getOrgCustomForm()
      this.formsByType = this.allForms.filter(f => f['resource'] == this.resource)
    } catch (error) {
      console.log(error)
    }
    this.toggleSelectedTab('MEETING_REVIEW')
  },
  computed: {
    ...mapState(['user']),
  },
  methods: {
    toggleSelectedTab(tab) {
      this.selectedTab = tab
    },
    fnTest(event) {
      this.selectedForm = event
      let index = this.formsByType.findIndex(f => f.id == this.selectedForm.id)
      console.log(index)
      console.log(this.formsByType.length, 'bef')
      if (~index) {
        console.log('slcing and dicing')
        this.formsByType[index] = this.selectedForm
        this.formsByType = [...this.formsByType]
        console.log(this.formsByType)
      }
      console.log(this.formsByType)
      console.log(this.formsByType.length, 'after')
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
