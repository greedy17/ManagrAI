<template>
  <div class="container">
    <div class="box">
      <div class="box__header">
        <div class="box__title">Generate Story Report</div>
      </div>
      <div class="box__content">
        <div class="form">
          <!-- Select Representative -->
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

          <!-- Select Lead -->
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

          <!-- Submit -->
          <div class="form__element" style="margin-top: 1.5rem;">
            <button
              class="button"
              :disabled="!bothFieldsHaveSelections"
              @click.prevent="generateReport"
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
import Lead from '@/services/leads'
import StoryReport from '@/services/storyReports'
import { loadEntireCollection } from '@/services/utils'

export default {
  name: 'GenerateStoryReport',
  props: {
    representatives: {
      type: CollectionManager,
      required: true,
    },
  },
  data() {
    return {
      selectedRepresentative: null,
      selectedLead: null,
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
  methods: {
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

      this.selectedLead = null
      this.leads.filters.byUser = repID
      this.leads.filters.byStatus = this.getIsClosedStatus
      loadEntireCollection(this.leads)
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
