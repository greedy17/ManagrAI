<template>
  <div class="container">
    <div :key="i" class="box" v-for="(resource, i) in FORM_RESOURCES">
      <div @click="toggleSelectedFormResource(resource)" class="box__header">
        <span class="box__title">
          {{ resource }}
        </span>
      </div>

      <div :ref="`${resource.toLowerCase()}-content`" class="box__content">
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
            Create {{ resource }} Form
          </div>
          <div
            class="box__tab"
            :class="{ 'box__tab--active': selectedTab == 'UPDATE' }"
            @click="toggleSelectedTab('UPDATE')"
          >
            Update {{ resource }} Form
          </div>
        </div>
        <div class="box__tab-content">
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

          <!--         <CustomSlackForm
            :show-validations="showValidations"
            :customForm="selectedForm"
            :formType="selectedTab"
            :resource="resource"
            v-on:update:selectedForm="updateForm($event)"
          /> -->
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CustomSlackForm from '@/views/settings/CustomSlackForm'
import { mapState } from 'vuex'
import SlackOAuth, { salesforceFields } from '@/services/slack'
const MEETING_REVIEW = 'MEETING_REVIEW'
const CREATE = 'CREATE'
const UPDATE = 'UPDATE'
const OPPORTUNITY = 'Opportunity'
const CONTACT = 'Contact'
const ACCOUNT = 'Account'
const FORM_RESOURCES = [OPPORTUNITY, ACCOUNT, CONTACT]
const FORM_TYPES = [MEETING_REVIEW, CREATE, UPDATE]
export default {
  name: 'SlackFormSettings',
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
      FORM_RESOURCES,
      FORM_TYPES,
    }
  },
  watch: {},
  async created() {
    try {
      this.allForms = await SlackOAuth.api.getOrgCustomForm()

      this.formsByType = this.allForms.filter(f => f['resource'] == this.resource)

      //this.toggleSelectedTab('MEETING_REVIEW')
    } catch (error) {
      console.log(error)
    }
  },
  computed: {
    ...mapState(['user']),
  },
  methods: {
    toggleSelectedFormResource(resource) {
      if (this.resource && resource) {
        if (this.resource == resource) {
          // toggle to open and close if the same expand is clicked
          let classList = this.$refs[`${resource.toLowerCase()}-content`][0].classList
          if (classList.contains('box__content--expanded')) {
            classList.toggle('box__content--closed')
            classList.toggle('box__content--expanded')
          } else if (classList.contains('box__content--closed')) {
            classList.toggle('box__content--expanded')
            classList.toggle('box__content--closed')
          } else {
            classList.toggle('box__content--expanded')
          }
        } else {
          let prev = this.resource
          this.resource = resource
          let prevClassList = this.$refs[`${prev.toLowerCase()}-content`][0].classList
          let classList = this.$refs[`${this.resource.toLowerCase()}-content`][0].classList
          if (prevClassList.contains('box__content--expanded')) {
            prevClassList.toggle('box__content--closed')
            prevClassList.toggle('box__content--expanded')
          }
          classList.toggle('box__content--expanded')
        }
      }
    },
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

.box__content {
  display: none;
  &--closed {
    animation: closemenu forwards;
    animation-duration: 0.5s;
    animation-iteration-count: 1;
    display: block;
  }
}
.box__content--expanded {
  max-height: 90vh;
  display: block;
  animation: expandmenu forwards;
  animation-duration: 1.5s;
  animation-iteration-count: 1;
  overflow-y: scroll;
}
@keyframes expandmenu {
  0% {
    height: 0rem;
    opacity: 0;
  }
  100% {
    height: 50rem;
    opacity: 1;
  }
}

@keyframes closemenu {
  0% {
    height: 50rem;
    opacity: 0.01;
  }
  100% {
    height: 0rem;
    opacity: 0;
  }
}
</style>
