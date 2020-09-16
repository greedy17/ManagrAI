<template>
  <div class="custom-fields">
    Custom Fields

    <!-- Company Size -->
    <div class="field section-shadow">
      <div class="label">Company Size</div>
      <div class="dropdown-container">
        <select v-model="lead.companySize">
          <option
            v-for="(option, i) in LeadModel.COMPANY_SIZE_CHOICES"
            :value="option.value"
            :key="i"
          >
            {{ option.label }}
          </option>
        </select>
      </div>
    </div>

    <!-- Industry -->
    <div class="field section-shadow">
      <div class="label">Industry</div>
      <div class="dropdown-container">
        <select v-model="lead.industry">
          <option v-for="(option, i) in LeadModel.INDUSTRY_CHOICES" :value="option.value" :key="i">
            {{ option.label }}
          </option>
        </select>
      </div>
    </div>

    <!-- Competitor -->
    <div class="field section-shadow">
      <div class="label">Competitor</div>
      <div class="dropdown-container">
        <select v-model="lead.competitor">
          <option
            v-for="(option, i) in LeadModel.COMPETITOR_CHOICES"
            :value="option.value"
            :key="i"
          >
            {{ option.label }}
          </option>
        </select>
      </div>
      Text Field Here
    </div>

    <!-- Geography -->
    <div class="field section-shadow">
      <div class="label">Geography</div>
      Text Field Here
    </div>

    <!-- Type -->
    <div class="field section-shadow">
      <div class="label">Type</div>
      <div class="dropdown-container">
        <select v-model="lead.type">
          <option v-for="(option, i) in LeadModel.TYPE_CHOICES" :value="option.value" :key="i">
            {{ option.label }}
          </option>
        </select>
      </div>
    </div>

    <!-- Custom -->
    <div class="field section-shadow">
      <div class="label">Custom</div>
      Text Field Here
    </div>
  </div>
</template>

<script>
import LeadModel from '@/services/leads'

export default {
  name: 'LeadCustomFields',
  components: {},
  props: {
    lead: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      LeadModel,
    }
  },
  created() {},
  computed: {},
  methods: {},
  watch: {
    // watch fields for changes--> patch API if change
    'lead.companySize': (newVal, oldVal) => {},
    'lead.industry': (newVal, oldVal) => {},
  },
}
</script>

<style scoped lang="scss">
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.custom-fields {
  @include standard-border();
  background-color: $white;
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.05);
  min-height: 50rem;
  display: flex;
  flex-flow: column;
}

.custom-fields,
.custom-fields > * {
  @include base-font-styles();
  line-height: 1.14;
  color: $main-font-gray;
  font-size: 1rem;
}

.field {
  display: flex;
  flex-flow: column;
  justify-content: center;
  padding: 1.2rem 0;

  .label {
    text-align: center;
    margin-bottom: 0.5rem;
  }

  .dropdown-container {
    box-sizing: border-box;
    display: flex;
    flex-flow: row;
    select {
      background-color: rgba($color: $dark-gray-blue, $alpha: 0);
      border: 0;
      color: $main-font-gray;
      border-radius: 0.5rem;
      padding: 0.5rem;
      font-size: 1rem;
      font-weight: 600;
      margin-left: auto;
      margin-right: 1rem;
      width: 75%;

      option {
        padding-top: 1rem;
      }
    }
  }
}
</style>
