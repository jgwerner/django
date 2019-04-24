import styled from 'styled-components/macro'
import { width, space, borders, textAlign, verticalAlign, WidthProps, SpaceProps, BordersProps, TextAlignProps, VerticalAlignProps } from 'styled-system'

interface TableProps extends WidthProps, SpaceProps, BordersProps, TextAlignProps, VerticalAlignProps {
  striped?: boolean
}

const Table = styled.table<TableProps>(
  {
    borderCollapse: 'collapse'
  },
  width,
  borders,
  space
)

export const TableHeader = styled.th<TableProps>(
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

export const TableData = styled.td<TableProps>(
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

const striped = (props: TableProps) =>
  props.striped
    ? {
        '&:nth-child(even)': {
          backgroundColor: '#f2f2f2'
        }
      }
    : null

export const TableRow = styled.tr<TableProps>(striped, space)


Table.displayName = 'Table'

Table.defaultProps = {
  m: 'auto',
  width: '100%',
  border: '1px solid rgba(0, 0, 0, 0.15)'
}

TableData.defaultProps = {
  textAlign: 'left',
  p: 3
}

TableHeader.defaultProps = {
  textAlign: 'left',
  p: 3
}

export default Table
