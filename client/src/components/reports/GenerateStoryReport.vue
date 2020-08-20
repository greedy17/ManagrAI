<template>
  <div class="container">
    <div class="box">
      <div class="box__header">
        <div class="box__title">Generate Story Report</div>
      </div>
      <div class="box__content">
        <div class="form">
          <div class="form__element">
            <div class="form__element-header">Select Representative</div>
            <select class="select" v-if="representatives.refreshing" disabled>
              <option>Loading...</option>
            </select>
            <select class="select" v-else v-model="selectedRepresentative">
              <option disabled :value="null">Select Representative</option>
              <option v-for="rep in representatives.list" :key="rep.id" :value="rep.id">
                {{ rep.fullName.trim() ? rep.fullName : rep.email }}
              </option>
            </select>
          </div>
          <div class="form__element" style="margin-top: 1.5rem;">
            <div class="form__element-header">Lead Closed</div>
            <select class="select" v-if="leads.refreshing" disabled>
              <option disabled>Loading...</option>
            </select>
            <select class="select" v-else v-model="selectedLead" :disabled="!leads.list.length">
              <option disabled :value="null">Select Lead</option>
              <option v-for="lead in leads.list" :key="lead.id" :value="lead.id">
                {{ lead.title }}
              </option>
            </select>
          </div>
          <div class="form__element" style="margin-top: 1.5rem;">
            <ComponentLoadingSVG style="margin: unset" v-if="loading" />
            <button
              class="button"
              :disabled="!bothFieldsHaveSelections"
              @click.prevent="generateReport"
              v-else
            >
              Generate Report
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CollectionManager from '@/services/collectionManager'
import User from '@/services/users'
import Lead from '@/services/leads'
import StoryReport from '@/services/storyReports'

export default {
  name: 'GenerateStoryReport',
  data() {
    return {
      selectedRepresentative: null,
      selectedLead: null,
      loading: false,
      representatives: CollectionManager.create({
        ModelClass: User,
        filters: {
          byUser: this.$store.state.user.id,
        },
      }),
      leads: CollectionManager.create({
        ModelClass: Lead,
        filters: {
          byUser: this.$store.state.user.id,
          byStatus: this.getIsClosedStatus,
          orderBy: '-expected_close_date',
        },
      }),
    }
  },
  created() {
    this.loadEntireCollection(this.representatives)
  },
  methods: {
    async loadEntireCollection(collection) {
      // Since the list of collection is for populating a dropdown, there is no pagination UI.
      // Yet, our backend delivers paginated results.
      // Therefore, continue to retrieve (and append) more results as long as this collection has a next page.
      await collection.refresh()
      while (collection.pagination.hasNextPage) {
        await collection.addNextPage()
      }
    },
    generateReport() {
      StoryReport.api.create(this.selectedLead).then(() => {
        this.clearForm()
        this.$Alert.alert({
          type: 'success',
          timeout: 3000,
          message: `Report being generated! You will receive an email once the report is accessible.`,
        })
      })
    },
    clearForm() {
      this.selectedLead = null
      this.leads.list = []
      this.selectedRepresentative = null
    },
  },
  watch: {
    selectedRepresentative(repID) {
      if (repID === null) {
        return
      }
      this.leads.pagination.page = 1
      this.leads.list = []
      this.selectedLead = null
      this.leads.filters.byUser = repID
      this.leads.filter.byStatus = this.getIsClosedStatus
      this.loadEntireCollection(this.leads)
    },
  },
  computed: {
    bothFieldsHaveSelections() {
      return !!this.selectedRepresentative && !!this.selectedLead
    },
    getStatuses() {
      return this.$store.state.stages
    },
    getIsClosedStatus() {
      return this.getStatuses.find(s => s.title == Lead.CLOSED).id
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/mixins/buttons';
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/mixins/inputs';
@import '@/styles/forms';

.container {
  width: 50vw;
}

.box__content {
  padding-left: 3em;
  padding-right: 3em;
}

.select {
  background-color: rgba($color: $dark-gray-blue, $alpha: 0);
  width: 100%;
  border: 2px solid $soft-gray;
  color: $main-font-gray;
  border-radius: 0.5rem;
  padding: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  margin-left: auto;
  height: 2.5rem;
}

select {
  &:disabled {
    background-color: $mid-gray;
  }

  option {
    padding-top: 1rem;
  }
}

.button {
  margin-left: auto;
  margin-right: 0;
}
</style>
