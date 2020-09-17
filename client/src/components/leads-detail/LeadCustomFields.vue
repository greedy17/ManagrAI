<template>
  <div class="custom-fields">
    <div class="header section-shadow">Custom Fields</div>

    <!-- Company Size -->
    <div class="dropdown-field section-shadow">
      <div class="label">Company Size</div>
      <div class="dropdown-container">
        <select v-model="lead.companySize">
          <option :value="null" :key="'null'" disabled>-Select Company Size-</option>
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
    <div class="dropdown-field section-shadow">
      <div class="label">Industry</div>
      <div class="dropdown-container">
        <select v-model="lead.industry">
          <option :value="null" :key="'null'" disabled>-Select Industry-</option>
          <option v-for="(option, i) in LeadModel.INDUSTRY_CHOICES" :value="option.value" :key="i">
            {{ option.label }}
          </option>
        </select>
      </div>
    </div>

    <!-- Competitor -->
    <div class="dropdown-field section-shadow">
      <div class="label">Competitor</div>
      <div class="dropdown-container">
        <select v-model="lead.competitor">
          <option :value="null" :key="'null'" disabled>-Select Competitor-</option>
          <option
            v-for="(option, i) in LeadModel.COMPETITOR_CHOICES"
            :value="option.value"
            :key="i"
          >
            {{ option.label }}
          </option>
        </select>
      </div>
      <!-- Competitor Description -->
      <div class="text-field" style="padding: 1rem 0 0 0;">
        <div class="display-mode-container" v-if="!competitorDescription.editing">
          <div class="value">{{ lead.competitorDescription || '-Empty-' }}</div>
          <div class="edit-icon-container">
            <img
              src="@/assets/images/pencil.svg"
              class="edit-icon"
              @click.stop.prevent="editTextField('competitorDescription')"
            />
          </div>
        </div>
        <div class="edit-mode-container" v-else-if="competitorDescription.editing">
          <form @submit.prevent="updateTextField('competitorDescription')">
            <input type="text" v-model="competitorDescription.temp" placeholder="Description" />
            <img
              class="save"
              src="@/assets/images/checkmark.svg"
              @click.stop.prevent="updateTextField('competitorDescription')"
            />
            <img
              class="reset"
              src="@/assets/images/remove.svg"
              @click.stop.prevent="resetTextField('competitorDescription')"
            />
          </form>
        </div>
      </div>
    </div>

    <!-- Geography -->
    <div class="text-field section-shadow">
      <div class="label">Geography</div>
      <div class="display-mode-container" v-if="!geography.editing">
        <div class="value">{{ lead.geographyAddress || '-Empty-' }}</div>
        <div class="edit-icon-container">
          <img
            src="@/assets/images/pencil.svg"
            class="edit-icon"
            @click.stop.prevent="editTextField('geography')"
          />
        </div>
      </div>
      <div class="edit-mode-container" v-else-if="geography.editing">
        <form @submit.prevent="updateGeography">
          <GmapAutocomplete :placeholder="'Geography'" @place_changed="setGeographyTemp" />
          <img
            class="save"
            src="@/assets/images/checkmark.svg"
            @click.stop.prevent="updateGeography"
          />
          <img
            class="reset"
            src="@/assets/images/remove.svg"
            @click.stop.prevent="resetGeography"
          />
        </form>
      </div>
    </div>

    <!-- Type -->
    <div class="dropdown-field section-shadow">
      <div class="label">Type</div>
      <div class="dropdown-container">
        <select v-model="lead.type">
          <option :value="null" :key="'null'" disabled>-Select Type-</option>
          <option v-for="(option, i) in LeadModel.TYPE_CHOICES" :value="option.value" :key="i">
            {{ option.label }}
          </option>
        </select>
      </div>
    </div>

    <!-- Custom -->
    <div class="text-field section-shadow">
      <div class="label">Custom</div>
      <div class="display-mode-container" v-if="!custom.editing">
        <div class="value">{{ lead.custom || '-Empty-' }}</div>
        <div class="edit-icon-container">
          <img
            src="@/assets/images/pencil.svg"
            class="edit-icon"
            @click.stop.prevent="editTextField('custom')"
          />
        </div>
      </div>
      <div class="edit-mode-container" v-else-if="custom.editing">
        <form @submit.prevent="updateTextField('custom')">
          <input type="text" v-model="custom.temp" placeholder="Custom" />
          <img
            class="save"
            src="@/assets/images/checkmark.svg"
            @click.stop.prevent="updateTextField('custom')"
          />
          <img
            class="reset"
            src="@/assets/images/remove.svg"
            @click.stop.prevent="resetTextField('custom')"
          />
        </form>
      </div>
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
      // Text fields:
      competitorDescription: {
        editing: false,
        temp: this.lead.competitorDescription,
      },
      geography: {
        editing: false,
        tempAddress: null,
        tempAddressComponents: {},
      },
      custom: {
        editing: false,
        temp: this.lead.custom,
      },
    }
  },
  watch: {
    // Change in dropdown-field --> patch Lead
    'lead.companySize': function(companySize) {
      this.updateLead({ companySize })
    },
    'lead.industry': function(industry) {
      this.updateLead({ industry })
    },
    'lead.competitor': function(competitor) {
      this.updateLead({ competitor })
    },
    'lead.type': function(type) {
      this.updateLead({ type })
    },
  },
  methods: {
    updateLead(data) {
      return LeadModel.api.update(this.lead.id, data)
    },
    editTextField(field) {
      this[field].editing = true
    },
    updateTextField(field) {
      let data = {
        [field]: this[field].temp,
      }
      this.updateLead(data)
        .then(() => {
          this.lead[field] = this[field].temp
        })
        .finally(() => {
          this.resetTextField(field)
        })
    },
    resetTextField(field) {
      this[field].editing = false
      this[field].temp = this.lead[field]
    },
    setGeographyTemp({ formatted_address, address_components, geometry: { location } }) {
      let streetNumber = this.getAddressComponent('street_number', address_components)
      let route = this.getAddressComponent('route', address_components)
      let locality = this.getAddressComponent('locality', address_components)
      let administrativeAreaLevel3 = this.getAddressComponent(
        'administrative_area_level_3',
        address_components,
      )
      let administrativeAreaLevel2 = this.getAddressComponent(
        'administrative_area_level_2',
        address_components,
      )
      let administrativeAreaLevel1 = this.getAddressComponent(
        'administrative_area_level_1',
        address_components,
      )
      let country = this.getAddressComponent('country', address_components)
      let postalCode = this.getAddressComponent('postal_code', address_components)
      let latitude = location.lat()
      let longitude = location.lng()

      this.geography.tempAddress = formatted_address
      this.geography.tempAddressComponents = {
        streetNumber,
        route,
        locality,
        administrativeAreaLevel3,
        administrativeAreaLevel2,
        administrativeAreaLevel1,
        country,
        postalCode,
        latitude,
        longitude,
      }
    },
    getAddressComponent(target, allComponents) {
      // Look through geodata address_components for component whose 'type' matches
      // return both long and short names for the component
      // null if not found
      for (let c of allComponents) {
        if (c.types.includes(target)) {
          return {
            longName: c.long_name,
            shortName: c.short_name,
          }
        }
      }
      return null
    },
    updateGeography() {
      let data = {
        geographyAddress: this.geography.tempAddress,
        geographyAddressComponents: this.geography.tempAddressComponents,
      }
      this.updateLead(data)
        .then(({ geographyAddress, geographyAddressComponents }) => {
          this.lead.geographyAddress = geographyAddress
          this.lead.geographyAddressComponents = geographyAddressComponents
        })
        .finally(() => {
          this.resetGeography()
        })
    },
    resetGeography() {
      this.geography.editing = false
      this.geography.tempAddress = null
      this.geography.tempAddressComponents = {}
    },
  },
}
</script>

<style scoped lang="scss">
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/utils';

.custom-fields {
  @include standard-border();
  background-color: $white;
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.05);
  display: flex;
  flex-flow: column;
}

.custom-fields,
.custom-fields > * {
  @include base-font-styles();
  line-height: 1.14;
  color: $main-font-gray;
  font-size: 0.875rem;
}

.header {
  padding: 1rem 0;
  text-align: center;
  font-weight: 600;
  font-size: 1rem;
}

.dropdown-field {
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
      @include pointer-on-hover;
      background-color: rgba($color: $dark-gray-blue, $alpha: 0);
      border: 0;
      color: $gray;
      border-radius: 0.5rem;
      padding: 0.5rem;
      font-size: 0.875rem;
      margin: 0 1.5rem;
      flex-grow: 1;
    }
  }
}

.text-field {
  display: flex;
  flex-flow: column;
  align-items: center;
  justify-content: center;
  padding: 1.2rem 0;

  .label {
    text-align: center;
    margin-bottom: 0.5rem;
  }

  .display-mode-container {
    color: rgba($color: $main-font-gray, $alpha: 0.5);
    padding: 0.5rem 0;
    width: 100%;
    display: flex;
    flex-flow: row;
    align-items: center;

    .value {
      margin-left: 1.5rem;
      padding-left: 0.5rem;
      flex-grow: 1;
      max-width: 8.5rem;
      word-wrap: break-word;
    }

    .edit-icon-container {
      margin: 0 1.5rem 0 auto;
    }

    .edit-icon {
      @include pointer-on-hover;
      opacity: 0.4;
      height: 1.2rem;
      width: 1.2rem;

      &:hover {
        opacity: 1;
      }
    }
  }

  .edit-mode-container {
    width: 100%;
  }

  form {
    display: flex;
    flex-flow: row;
    align-items: center;
    width: 100%;
    box-sizing: border-box;
    padding: 0.25rem 0;

    input {
      @include input-field();
      margin-left: 1rem;
      width: 8.5rem;
    }

    .save {
      background-color: $dark-green;
      border-radius: 3px;
      margin-left: auto;
    }

    .reset {
      background-color: $silver;
      border-radius: 3px;
      margin: 0 1rem 0 0.5rem;
    }
  }
}
</style>
