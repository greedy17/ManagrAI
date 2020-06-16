<template>
  <div class="status-dropdown">
    <select
      v-model="selectedStatus"
      :style="computedStyles"
      :disabled="disabled || selectedStatus === 'CLOSED'"
    >
      <option :value="null">---</option>
      <option v-for="option in statusEnums" :key="option" :value="option.toUpperCase()">
        {{ option }}
      </option>
    </select>
    <Modal v-if="modal.isOpen" dimmed @close-modal="closeModal" :width="50">
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
      selectedStatus: this.lead.status,
      modal: {
        isOpen: false,
      },
    }
  },
  methods: {
    updateStatus(newStatus) {
      let patchData = { status: newStatus }
      Lead.api.update(this.lead.id, patchData).then(lead => {
        this.lead.status = lead.status
      })
    },
    closeModal() {
      let selectedStatus = this.selectedStatus ? this.selectedStatus.toUpperCase() : null
      let leadStatus = this.lead.status ? this.lead.status.toUpperCase() : null
      if (selectedStatus != leadStatus) {
        this.selectedStatus = this.lead.status
      }
      this.modal.isOpen = false
    },
  },
  computed: {
    computedStyles() {
      return getStatusPrimaryColor(this.lead.status) // returns a plain-object with the key/val of backgroundColor: '#<HEX>'
    },
  },
  watch: {
    selectedStatus(newStatus, oldStatus) {
      if (newStatus == oldStatus) {
        return
      }
      if (newStatus != 'CLOSED') {
        this.updateStatus(newStatus)
      } else {
        this.modal.isOpen = true
      }
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
