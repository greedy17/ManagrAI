<template>
  <div>
    <div
      class="field-container"
      v-if="dataType === 'TextArea' || dataType === 'String' || dataType.toLowerCase() === 'email'"
    >
      <textarea
        @input=";(value = $event.target.value), setUpdateValues(apiName, value)"
        :disabled="inlineLoader"
        class="inline-input"
        :value="inlinePlaceholder"
        :name="apiName"
        v-autoresize
        autofocus="true"
        rows="1"
      />

      <div :class="{ disabled: inlineLoader }" class="save-close">
        <div @click="inlineUpdate" class="save">
          <span v-if="!inlineLoader">save</span>
          <img
            class="rotate disabled"
            v-else
            src="@/assets/images/refresh.svg"
            height="11px"
            alt=""
          />
        </div>
        <!-- <div :class="{ disabled: inlineLoader }" @click="closeInline" class="close">
          <span>close</span>
        </div> -->
      </div>
    </div>

    <div
      class="field-container"
      v-else-if="
        dataType === 'Date' ||
        dataType === 'Datetime' ||
        dataType === 'Double' ||
        dataType === 'Currency' ||
        dataType === 'Int'
      "
    >
      <input
        class="inline-input"
        v-if="dataType !== 'Double' || dataType !== 'Currency' || dataType !== 'Int'"
        :value="inlinePlaceholder"
        :type="dataType"
        @input=";(value = $event.target.value), setUpdateValues(apiName, value)"
        :disabled="inlineLoader"
      />
      <input
        :value="inlinePlaceholder"
        @input=";(value = $event.target.value), setUpdateValues(apiName, value)"
        :disabled="inlineLoader"
        class="inline-input"
        v-else
        type="number"
      />

      <div :class="{ disabled: inlineLoader }" class="save-close">
        <div @click="inlineUpdate" class="save">
          <span v-if="!inlineLoader">save</span>
          <img
            class="rotate disabled"
            v-else
            src="@/assets/images/refresh.svg"
            height="11px"
            alt=""
          />
        </div>
        <!-- <div :class="{ disabled: inlineLoader }" @click="closeInline" class="close">
          <span>close</span>
        </div> -->
      </div>
    </div>

    <div
      class="field-container"
      v-else-if="dataType === 'Picklist' || dataType === 'MultiPicklist'"
    >
      <Multiselect
        :options="
          apiName === 'dealstage'
            ? field.options[0][resource.secondary_data.pipeline]
              ? field.options[0][resource.secondary_data.pipeline].stages
              : []
            : picklistOptions[field.id] || field.options
        "
        :placeholder="inlinePlaceholder || '-'"
        selectLabel=""
        :track-by="apiName === 'dealstage' ? 'id' : 'value'"
        label="label"
        :multiple="dataType === 'MultiPicklist' ? true : false"
        v-model="selectedOption"
        :disabled="inlineLoader"
        selectedLabel=""
        deselectLabel=""
        @select="
          setUpdateValues(
            apiName === 'ForecastCategory' ? 'ForecastCategoryName' : field.apiName,
            apiName === 'dealstage' ? $event.id : $event.value,
            dataType === 'MultiPicklist' ? true : false,
          )
        "
      >
        <template slot="noResult">
          <p class="multi-slot">No results.</p>
        </template>
      </Multiselect>

      <div :class="{ disabled: inlineLoader }" class="save-close">
        <div @click="inlineUpdate" class="save">
          <span v-if="!inlineLoader">save</span>
          <img
            class="rotate disabled"
            v-else
            src="@/assets/images/refresh.svg"
            height="11px"
            alt=""
          />
        </div>
        <!-- <div :class="{ disabled: inlineLoader }" @click="closeInline" class="close">
          <span>close</span>
        </div> -->
      </div>
    </div>

    <div class="field-container" v-else-if="dataType === 'Boolean'">
      <Multiselect
        :options="booleans"
        :placeholder="inlinePlaceholder || '-'"
        selectLabel=""
        v-model="selectedOption"
        :disabled="inlineLoader"
        selectedLabel=""
        deselectLabel=""
        @select="
          setUpdateValues(apiName, $event.value, dataType === 'MultiPicklist' ? true : false)
        "
      >
        <template slot="noResult">
          <p class="multi-slot">No results.</p>
        </template>
      </Multiselect>

      <div :class="{ disabled: inlineLoader }" class="save-close">
        <div @click="inlineUpdate" class="save">
          <span v-if="!inlineLoader">save</span>
          <img
            class="rotate disabled"
            v-else
            src="@/assets/images/refresh.svg"
            height="11px"
            alt=""
          />
        </div>
        <!-- <div :class="{ disabled: inlineLoader }" @click="closeInline" class="close">
          <span>close</span>
        </div> -->
      </div>
    </div>

    <div class="field-container" v-else-if="dataType === 'Reference'">
      <Multiselect
        :options="referenceOpts"
        :placeholder="loadingOptions ? 'Gathering options...' : inlinePlaceholder || '-'"
        selectLabel=""
        track-by="id"
        label="name"
        selectedLabel=""
        deselectLabel=""
        v-model="selectedOption"
        :disabled="inlineLoader || loadingOptions"
        :loading="loadingOptions"
        @select="setUpdateValues(apiName, $event.id, false)"
        @open="getReferenceOptions(field.id)"
      >
        <template slot="noResult">
          <p class="multi-slot">No results.</p>
        </template>
      </Multiselect>

      <div :class="{ disabled: inlineLoader }" class="save-close">
        <div @click="inlineUpdate" class="save">
          <span v-if="!inlineLoader">save</span>
          <img
            class="rotate disabled"
            v-else
            src="@/assets/images/refresh.svg"
            height="11px"
            alt=""
          />
        </div>
        <!-- <div :class="{ disabled: inlineLoader }" @click="closeInline" class="close">
          <span>close</span>
        </div> -->
      </div>
    </div>

    <div class="field-container" v-else>...</div>
  </div>
</template>

<script>
import { CRMObjects } from '@/services/crm'
import { SObjects } from '@/services/salesforce'

export default {
  name: 'InlineFieldEditor',
  data() {
    return {
      formData: {},
      inlineLoader: false,
      selectedOption: null,
      booleans: ['true', 'false'],
      loadingOptions: false,
      referenceOpts: [],
    }
  },
  components: {
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  props: {
    dataType: {
      type: String,
    },
    apiName: {
      type: String,
    },
    inlinePlaceholder: {
      type: String,
    },
    integrationId: {
      type: String,
    },
    resourceId: {
      type: String,
    },
    resourceType: {
      type: String,
    },
    resource: {},
    field: {},
  },
  methods: {
    setUpdateValues(key, val, multi) {
      if (multi) {
        this.formData[key] = this.formData[key]
          ? this.formData[key] + ';' + val
          : val.split(/&#39;/g)[0]
      } else {
        this.formData[key] = val
      }
    },
    closeInline() {
      this.$emit('close-inline')
    },
    async inlineUpdate() {
      this.inlineLoader = true
      try {
        const res = await CRMObjects.api.updateResource({
          form_data: this.formData,
          resource_type: this.resourceType,
          form_type: 'UPDATE',
          resource_id: this.resourceId,
          integration_ids: [this.integrationId],
          from_workflow: false,
          workflow_title: 'None',
        })
      } catch (e) {
        console.log(e)
      } finally {
        setTimeout(() => {
          this.inlineLoader = false
          this.closeInline()
          this.$emit('setFields')
        }, 1000)
      }
    },
    async getReferenceOptions(id) {
      this.loadingOptions = true
      try {
        let res = await SObjects.api.getSobjectPicklistValues({
          sobject_id: id,
          value: '',
          for_filter: null,
        })

        this.referenceOpts = res
      } catch (e) {
        console.log(e)
      } finally {
        setTimeout(() => {
          this.loadingOptions = false
        })
      }
    },
  },
  computed: {
    picklistOptions() {
      return this.$store.state.allPicklistOptions
    },
  },
  directives: {
    autoresize: {
      inserted(el) {
        function adjustTextareaHeight() {
          el.style.height = 'auto'
          el.style.height = el.scrollHeight + 'px'
        }

        el.addEventListener('input', adjustTextareaHeight)
        el.addEventListener('focus', adjustTextareaHeight)
        adjustTextareaHeight()
      },
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

::v-deep .multiselect * {
  font-size: 13px;
  font-family: $base-font-family;
  border-radius: 5px !important;
}
::v-deep .multiselect__option--highlight {
  background-color: $off-white;
  color: $base-gray;
}
::v-deep .multiselect__option--selected {
  background-color: $soft-gray;
}

::v-deep .multiselect__content-wrapper {
  border-radius: 5px;
  margin: 0.5rem 0rem;
  border-top: 1px solid $soft-gray;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}
::v-deep .multiselect__placeholder {
  color: $base-gray;
}

.inline-input {
  outline: none;
  padding: 0.5rem 0.75rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  color: $base-gray;
  width: 100%;
  font-family: $base-font-family;
  font-size: 12px;
  line-height: 1.5;
  letter-spacing: 0.4px;
  resize: none;
}

::-webkit-calendar-picker-indicator {
  filter: invert(40%);
  cursor: pointer;
}

.field-container {
  position: relative;
  padding-top: 1rem;
  border-radius: 4px;
}

.save-close {
  position: absolute;
  right: 0;
  top: -1.5rem;
  display: flex;
  flex-direction: row;
  align-items: center;
}

.close {
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  outline: 1px solid rgba(0, 0, 0, 0.1);
  color: $coral;
  width: 36px;
  height: 20px;
  border-radius: 3px;
  cursor: pointer;
  margin-left: 0.5rem;
  margin-right: 2px;
  font-size: 11px;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 3px 6px 0 $very-light-gray;
    scale: 1.025;
  }
}

.save {
  display: flex;
  align-items: center;
  justify-content: center;
  background: $dark-green;
  outline: 1px solid $dark-green;
  color: white;
  width: 60px;
  height: 24px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 11px;
  transition: all 0.3s;
  margin-right: 4px;

  &:hover {
    box-shadow: 0 3px 6px 0 $very-light-gray;
    scale: 1.025;
  }
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  // background-color: $soft-gray;
  border-radius: 6px;
  padding: 0.75rem 0.75rem;
}

.dot {
  width: 6px;
  height: 6px;
  margin: 0 5px;
  background: rgb(97, 96, 96);
  border-radius: 50%;
  animation: bounce 1.2s infinite ease-in-out;
}

.dot:nth-child(2) {
  animation-delay: -0.4s;
}

.dot:nth-child(3) {
  animation-delay: -0.2s;
}

button {
  @include chat-button();
  padding: 0.5rem;
  margin-top: 0.5rem;
  background-color: $dark-green;
  color: white;
  border: none;
  font-size: 12px;
}

.flex-end {
  display: flex;

  align-items: center;
}

.disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}

.rotate {
  animation: rotation 1s infinite linear;
}
</style>