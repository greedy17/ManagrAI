<template>
  <div class="status-dropdown">
    <select
      :value="lead.status"
      :style="computedStyles"
      :disabled="disabled || lead.status === 'CLOSED'"
      @change="onChange"
    >
      <option :value="null">---</option>
      <option v-for="option in statusEnums" :key="option" :value="option.toUpperCase()">
        {{ option }}
      </option>
    </select>
    <Modal
      v-if="modal.isOpen"
      dimmed
      @close-modal="closeModal"
      @closed-lead="$emit('closed-lead')"
      :width="50"
    >
      <CloseLead :lead="lead" />
    </Modal>
  </div>
</template>

<script>
import { getStatusPrimaryColor } from '@/services/getColorFromLeadStatus'
import { statusEnums } from '@/services/leads/enumerables'
import Lead from '@/services/leads'
import CloseLead from '@/components/shared/CloseLead'

export default {
  name: 'LeadStatusDropdown',
  components: { CloseLead },
  props: {
    lead: {
      required: true,
      type: Object,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      statusEnums,
      modal: {
        isOpen: false,
      },
    }
  },
  methods: {
    onChange({ target: { value } }) {
      if (value != 'CLOSED') {
        this.updateStatus(value)
      } else {
        this.modal.isOpen = true
      }
    },
    updateStatus(newStatus) {
      let patchData = { status: newStatus }
      Lead.api.update(this.lead.id, patchData).then(lead => {
        this.lead.status = lead.status
        this.lead.statusLastUpdate = lead.statusLastUpdate
      })
    },
    closeModal() {
      this.modal.isOpen = false
    },
  },
  computed: {
    computedStyles() {
      return getStatusPrimaryColor(this.lead.status) // returns a plain-object with the key/val of backgroundColor: '#<HEX>'
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.status-dropdown {
  width: 6.25rem;
  height: 1.25rem;
  background-color: rgba(0, 0, 0, 0); // rgb irrelevant, this is for the alpha / transparency

  select {
    @include pointer-on-hover();
    @include base-font-styles();
    width: 96%;
    height: 100%;
    padding: 0.125rem 1rem;
    line-height: 1.6;
    color: $white;
    font-size: 10px;
    font-weight: bold;
    border: unset;

    &:focus {
      outline: none;
    }
  }
}
</style>
