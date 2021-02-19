<template>
  <div class="container">
    <div class="box">
      <div @click="toggleSelectedFormResource('Opportunity')" class="box__header">
        <span class="box__title">
          Opportunity
        </span>
      </div>
      <template>
        <div ref="opportunity-content" class="box__content box__content--expanded">
          <template v-if="formsByType.length">
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
            <div class="box__tab-content">
              <p>
                <i
                  >Required Fields have been pre-filled as part of the form, add or remove
                  additional fields</i
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
            </div>
          </template>
          <template v-else>
            <p>
              <i
                >We are currently gathering your fields and creating your forms, please check back
                in a couple of minutes</i
              >
            </p>
          </template>
        </div>
      </template>
    </div>
    <div class="box">
      <div @click="toggleSelectedFormResource('Account')" class="box__header">
        <span class="box__title">
          Account
        </span>
      </div>
      <template>
        <div ref="account-content" class="box__content">
          <template v-if="formsByType.length">
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
            <div class="box__tab-content">
              <p>
                <i
                  >Required Fields have been pre-filled as part of the form, add or remove
                  additional fields</i
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
            </div>
          </template>
          <template v-else>
            <p>
              <i
                >We are currently gathering your fields and creating your forms, please check back
                in a couple of minutes</i
              >
            </p>
          </template>
        </div>
      </template>
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
  watch: {
    resource: {
      handler(val, curr) {
        if (val == curr) {
          this.$refs[`${val.toLowerCase()}-content`].classList.add('box__content--expanded')
        } else {
          if (curr) {
            this.$refs[`${curr.toLowerCase()}-content`].classList.remove('box__content--expanded')
          }
          this.$refs[`${val.toLowerCase()}-content`].classList.add('box__content--expanded')
        }
      },
    },
  },
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
    toggleSelectedFormResource(resource) {
      this.resource = resource
      this.formsByType = this.allForms.filter(f => {
        return f['resource'] == this.resource
      })
      this.toggleSelectedTab('MEETING_REVIEW')
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
  height: 0rem;
}
.box__content--expanded {
  display: block;
  max-height: 50rem;
  animation: expandmenu forwards;
  animation-duration: 1s;
  animation-iteration-count: 1;
}
@keyframes expandmenu {
  0% {
    height: 1rem;
  }
  100% {
    height: 50rem;
  }
}
</style>
