import styled from 'styled-components/macro'
import { width, space, borders, textAlign, verticalAlign } from 'styled-system'

const Table = styled.table(
  {
    borderCollapse: 'collapse'
  },
  width,
  borders,
  space
)

const Header = styled.th(
  {
    height: '30px',
    borderBottom: '1px solid rgba(0, 0, 0, 0.15)',
    // borderLeft: '1px solid rgba(0, 0, 0, 0.15)',
    padding: '5px 0 5px 10px',
    backgroundColor: '#f2f2f2'
  },
  textAlign,
  space,
  width,
  borders
)

const Data = styled.td(
  {
    height: '30px',
    // borderLeft: '1px solid rgba(0, 0, 0, 0.15)',
    padding: '5px 0 5px 10px'
  },
  textAlign,
  verticalAlign,
  space,
  width,
  borders
)

const striped = props =>
  props.striped
    ? {
        '&:nth-child(even)': {
          backgroundColor: '#f2f2f2'
        }
      }
    : null

const Row = styled.tr(striped, space)

Table.Header = Header
Table.Data = Data
Table.Row = Row

Table.displayName = 'Table'

Table.defaultProps = {
  m: 'auto',
  width: '100%',
  border: '1px solid rgba(0, 0, 0, 0.15)'
}

Table.Data.defaultProps = {
  textAlign: 'left',
  p: 3
}

Table.Header.defaultProps = {
  textAlign: 'left',
  p: 3
}

export default Table
