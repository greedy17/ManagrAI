import Pagination from '@/services/pagination'
import { apiErrorHandler } from '@/services/api'

/**
 * An abstraction that provides a simple interface for managing
 * paginated collections of entities from the API.
 **/
export default class CollectionManager {
  constructor({
    list = [],
    pagination = Pagination.create(),
    refreshing = false,
    loadingNextPage = false,
    filters = {},
    ModelClass = null,
  } = {}) {
    Object.assign(this, {
      list,
      pagination,
      refreshing,
      loadingNextPage,
      filters,
      ModelClass,
    })
  }

  // Factory Function
  static create(opts = {}) {
    opts = opts || {}
    return new CollectionManager(opts)
  }

  /**
   * Update the collection.
   *
   * @param {object} data - API response data
   * @param {boolean} append - Optional, add to the current list if `true`. Replace the
   *                           current list if false. Defaults to `false`.
   */
  update(data, append = false) {
    this.list = [...(append ? this.list : []), ...data.results]
    this.pagination = Pagination.create({
      ...this.pagination,
      next: data.next,
      previous: data.previous,
      totalCount: data.count,
    })
    return this
  }

  /**
   * Refresh the collection.
   */
  async refresh() {
    this.refreshing = true
    try {
      const response = await this.ModelClass.api.list({
        pagination: this.pagination,
        filters: this.filters,
      })
      return this.update(response)
    } catch (error) {
      apiErrorHandler({
        apiName: `Refresh ${this.ModelClass.name} Collection error`,
      })
    } finally {
      this.refreshing = false
    }
  }

  /**
   * Advance to the next page and refresh the collection.
   */
  nextPage() {
    this.pagination.setNextPage()
    return this.refresh()
  }

  /**
   * Go back to the previous page and refresh the collection.
   */
  prevPage() {
    this.pagination.setPrevPage()
    return this.refresh()
  }

  /**
   * Get the next page for a collection and add this page
   * to the collection.
   */
  async addNextPage() {
    if (this.pagination.next === null) {
      return
    }

    this.loadingNextPage = true
    this.pagination = {
      ...this.pagination,
      page: this.pagination.page + 1,
    }

    try {
      const response = await this.ModelClass.api.list({
        pagination: this.pagination,
        filters: this.filters,
      })
      return this.update(response, true)
    } catch (error) {
      apiErrorHandler({
        apiName: `Add Next Page for ${this.ModelClass.name} Collection error`,
      })
    } finally {
      this.loadingNextPage = false
    }
  }
}
