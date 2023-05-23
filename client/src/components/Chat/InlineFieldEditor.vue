<template>
  <div>
    <div
      class="field-container"
      v-if="dataType === 'TextArea' || dataType === 'String' || dataType.toLowerCase() === 'email'"
    >
      <textarea class="inline-input" :value="inlinePlaceholder" :name="apiName" rows="1" />
    </div>

    <div
      class="field-container"
      v-else-if="
        dataType === 'Date' ||
        dataType === 'Datetime' ||
        dataType === 'Double' ||
        dataType === 'Currency'
      "
    >
      <input
        class="inline-input"
        v-if="dataType !== 'Double' || dataType !== 'Currency'"
        :value="inlinePlaceholder"
        :type="dataType"
        @input=";(value = $event.target.value), setUpdateValues(apiName, value)"
      />
      <input class="inline-input" v-else type="number" />

      <button :class="{ loading: inlineLoader }" @click="inlineUpdate" type="submit">update</button>

      <!-- <div class="save-close">
        <span>x</span>
      </div> -->
    </div>

    <div
      class="field-container"
      v-else-if="dataType === 'Picklist' || dataType === 'MultiPicklist'"
    >
      picklist here
    </div>

    <div class="field-container" v-else-if="dataType === 'Reference'">{{ dataType }}</div>

    <div class="field-container" v-else>Can't update {{ dataType }} fields... yet</div>
  </div>
</template>

<script>
import { CRMObjects } from '@/services/crm'

export default {
  name: 'InlineFieldEditor',
  data() {
    return {
      formData: {},
      inlineLoader: false,
    }
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
  },
  methods: {
    setUpdateValues(key, val) {
      this.formData[key] = val
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

        console.log(res)
      } catch (e) {
        console.log(e)
      } finally {
        this.inlineLoader = false
        this.$emit('close-inline')
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.inline-input {
  outline: none;
  padding: 0.5rem 0.75rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  color: $base-gray;
}

::-webkit-calendar-picker-indicator {
  filter: invert(40%);
  cursor: pointer;
}

.field-container {
  position: relative;
}

.save-close {
  position: absolute;
  right: 0;
  top: 0;
}

.loading {
  color: red;
}
</style>